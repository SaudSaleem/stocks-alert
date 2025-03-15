<template>
  <div class="home-container flex flex-col">
    <div class="flex flex-row gap-2">
      <Button @click="showDrawer = true" style="width: 200px;">Open Drawer</Button>
      <Button @click="showCreateAlertDialog = true" style="width: 200px;">Create Alert</Button>
    </div>
    <Card v-if="user" class="welcome-card mt-8">
      <template #content>
        <div class="alerts-section">
          <Button @click="fetchAlerts" class="mb-4">Refresh Alerts</Button>
          <DataTable :value="alerts" stripedRows paginator :rows="5" tableStyle="min-width: 160rem">
            <Column field="ticker" header="Ticker" sortable></Column>
            <Column field="buy_price" header="Buy Price" sortable></Column>
            <Column field="current_price" header="Current Price" sortable></Column>
            <Column field="change_percentage" header="Change %" sortable>
              <template #body="slotProps">
                <span :class="slotProps.data.change_percentage >= 0 ? 'positive-change' : 'negative-change'">
                  {{ slotProps.data.change_percentage }}%
                </span>
              </template>
            </Column>
            <Column field="shares" header="Shares"></Column>
            <Column field="total_alerts_sent" header="Total Alerts Sent"></Column>
            <Column header="Status">
              <template #body="slotProps">
                <div class="status-indicators">
                  <span v-if="slotProps.data.is_sl_hit" class="status-badge sl-hit">SL Hit</span>
                  <span v-if="slotProps.data.is_tp1_hit" class="status-badge tp-hit">TP1 Hit</span>
                  <span v-if="slotProps.data.is_tp2_hit" class="status-badge tp-hit">TP2 Hit</span>
                  <span v-if="slotProps.data.is_tp3_hit" class="status-badge tp-hit">TP3 Hit</span>
                  <span v-if="slotProps.data.is_box_break_hit" class="status-badge box-break">Box Break</span>
                  <span v-if="slotProps.data.is_dip_buy_hit" class="status-badge dip-buy">Dip Buy</span>
                  <span v-if="slotProps.data.is_percentage_sl_hit" class="status-badge sl-hit">Percentage SL Hit</span>
                  <span v-if="slotProps.data.is_percentage_tp_hit" class="status-badge tp-hit">Percentage TP Hit</span>
                  <span v-if="slotProps.data.is_trailing_stop_hit" class="status-badge tp-hit">Trailing Stop Hit</span>
                </div>
              </template>
            </Column>
            <Column field="tp1" header="TP1 Price"></Column>
            <Column field="tp2" header="TP2 Price"></Column>
            <Column field="tp3" header="TP3 Price"></Column>
            <Column field="percentage_tp" header="TP %"></Column>
            <Column field="dip_buy" header="Dip Buy"></Column>
            <Column field="box_break" header="Box Break"></Column>
            <Column field="sl" header="SL"></Column>
            <Column field="percentage_sl" header="SL %"></Column>
            <Column field="notes" header="Notes"></Column>
            <Column field="date_added" header="Created At">
              <template #body="slotProps">
                {{ new Date(slotProps.data.date_added).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }) }}
              </template>
            </Column>
            <Column field="date_modified" header="Last Modified">
              <template #body="slotProps">
                {{ new Date(slotProps.data.date_modified).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }) }}
              </template>
            </Column>
            <Column field="update" header="Update">
              <template #body="slotProps">
                <Button @click="showUpdateAlertDialog = true; selectedAlert = {...slotProps.data}" label="Update" severity="warning" />
              </template>
            </Column>
            <Column field="delete" header="Delete">
              <template #body="slotProps">
                <Button @click="showDeleteAlertDialog = true; selectedAlert = slotProps.data" label="Delete" severity="danger" />
              </template>
            </Column>
          </DataTable>
        </div>
      </template>
    </Card>
    <Toast />
    <Drawer v-model:visible="showDrawer" :header="`Welcome, ${user?.name}`" :modal="true">
      <div class="user-info">
        <h3>Your information:</h3>
        <p><strong>Email:</strong> {{ user?.email }}</p>
        <p v-if="user?.name"><strong>Name:</strong> {{ user?.name }}</p>
        <p v-if="user?.phone"><strong>Phone:</strong> {{ user?.phone }}</p>
        <p><strong>Total Investment:</strong> {{ user?.total_investment }}</p>
        <p><strong>Current Value:</strong> {{ user?.current_value }}</p>
      </div>
      <div class="actions">
        <Button label="Logout" @click="logout" />
      </div>
    </Drawer>
    <Dialog v-model:visible="showCreateAlertDialog" :header="`Create Alert`" :modal="true" style="width: 50vw;">
      <div class="create-alert-form flex flex-wrap gap-2">
        <div class="flex flex-col gap-2 flex-1">
          <label for="ticker">Ticker</label>
          <Select v-model="alert.ticker" filter clearIcon :options="tickers" optionLabel="symbol" optionValue="symbol"
            placeholder="Select Ticker" class="flex-1">
          </Select>
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="buy_price">Buy Price</label>
          <InputNumber v-model="alert.buy_price" placeholder="Buy Price" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="tp1">TP1</label>
          <InputNumber v-model="alert.tp1" placeholder="TP1" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="tp2">TP2</label>
          <InputNumber v-model="alert.tp2" placeholder="TP2" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="tp3">TP3</label>
          <InputNumber v-model="alert.tp3" placeholder="TP3" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="sl">SL</label>
          <InputNumber v-model="alert.sl" placeholder="SL" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="percentage_tp">TP %</label>
          <InputNumber v-model="alert.percentage_tp" placeholder="TP %" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="box_break">Box Break</label>
          <InputNumber v-model="alert.box_break" placeholder="Box Break" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="dip_buy">Dip Buy</label>
          <InputNumber v-model="alert.dip_buy" placeholder="Dip Buy" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="percentage_sl">SL %</label>
          <InputNumber v-model="alert.percentage_sl" placeholder="SL %" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="trailing_stop_percentage">Trailing Stop %</label>
          <InputNumber v-model="alert.trailing_stop_percentage" placeholder="Trailing Stop %" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="shares">Shares</label>
          <InputNumber v-model="alert.shares" placeholder="Shares" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="notes">Notes</label>
          <InputText v-model="alert.notes" placeholder="Notes" class="flex-1" />
        </div>
      </div>
      <div class="w-full flex justify-center mt-3">
        <Button @click="createAlert" label="Create Alert" />
      </div>
    </Dialog>
    <Dialog v-model:visible="showDeleteAlertDialog" :header="`Delete Alert`" :modal="true" style="width: 50vw;">
      <div class="flex flex-col gap-2">
        <p style="text-align: center;">Are you sure you want to delete this alert?</p>
        <Button @click="deleteAlert(selectedAlert?.id)" class="mt-5" style="width: 100px; margin: 0 auto;" label="Delete" severity="danger" />
      </div>
    </Dialog>
    <Dialog v-model:visible="showUpdateAlertDialog" :header="`Update Alert`" :modal="true" style="width: 50vw;">
      <div class="update-alert-form flex flex-wrap gap-2">
        <div class="flex flex-col gap-2 flex-1">
          <label for="ticker">Ticker</label>
          <Select v-model="selectedAlert.ticker" disabled filter clearIcon :options="tickers" optionLabel="symbol" optionValue="symbol"
            placeholder="Select Ticker" class="flex-1">
          </Select>
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="buy_price">Buy Price</label>
          <InputNumber v-model="selectedAlert.buy_price" placeholder="Buy Price" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="tp1">TP1</label>
          <InputNumber v-model="selectedAlert.tp1" placeholder="TP1" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="tp2">TP2</label>
          <InputNumber v-model="selectedAlert.tp2" placeholder="TP2" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="tp3">TP3</label>
          <InputNumber v-model="selectedAlert.tp3" placeholder="TP3" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="percentage_tp">TP %</label>
          <InputNumber v-model="selectedAlert.percentage_tp" placeholder="TP %" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="box_break">Box Break</label>
          <InputNumber v-model="selectedAlert.box_break" placeholder="Box Break" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="dip_buy">Dip Buy</label>
          <InputNumber v-model="selectedAlert.dip_buy" placeholder="Dip Buy" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="sl">SL</label>
          <InputNumber v-model="selectedAlert.sl" placeholder="SL" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="percentage_sl">SL %</label>
          <InputNumber v-model="selectedAlert.percentage_sl" placeholder="SL %" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="trailing_stop_percentage">Trailing Stop %</label>
          <InputNumber v-model="selectedAlert.trailing_stop_percentage" placeholder="Trailing Stop %" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="shares">Shares</label>
          <InputNumber v-model="selectedAlert.shares" placeholder="Shares" class="flex-1" />
        </div>
        <div class="flex flex-col gap-2 flex-1">
          <label for="notes">Notes</label>
          <InputText v-model="selectedAlert.notes" placeholder="Notes" class="flex-1" />
        </div>
      </div>
      <div class="w-full flex justify-center mt-3">
        <Button @click="updateAlert" label="Update Alert" />
      </div>
    </Dialog>
  </div>
</template>

<script>
import axios from '../utils/axios';
import { useRouter } from 'vue-router';
import Card from 'primevue/card';
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Select from 'primevue/select';
import Drawer from 'primevue/drawer';
import Dialog from 'primevue/dialog';
import Column from 'primevue/column';
import Toast from 'primevue/toast';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
export default {
  name: 'HomeView',
  components: {
    Card,
    Button,
    DataTable,
    Column,
    Select,
    Drawer,
    Dialog,
    Toast,
    InputNumber,
    InputText
  },
  data() {
    return {
      user: null,
      showDrawer: false,
      showCreateAlertDialog: false,
      showDeleteAlertDialog: false,
      showUpdateAlertDialog: false,
      alerts: [],
      tickers: [],
      selectedAlert: null,
      alert: {
        ticker: "",
        buy_price: 0,
        tp1: null,
        tp2: null,
        tp3: null,
        box_break: null,
        dip_buy: null,
        sl: null,
        shares: null,
        percentage_tp: null,
        percentage_sl: null,
        notes: '',
        trailing_stop_percentage: null
      },
      pollingInterval: null,
      pollingDelay: 30000 // 30 seconds
    };
  },
  mounted() {
    // Get user from localStorage
    const userJson = localStorage.getItem('user');
    if (userJson) {
      this.user = JSON.parse(userJson);
      this.fetchAlerts();
      this.fetchTickers();
      // Start polling for alerts
      this.startPolling();
    } else {
      // Redirect to login if no user is found
      this.$router.push('/login');
    }
  },
  beforeUnmount() {
    // Clear polling interval when component is destroyed
    this.stopPolling();
  },
  watch: {
    'alert.ticker': async function (newVal) {
      const response = await this.getSelectedTickerInfo(newVal);
      this.alert.buy_price = Number(response.current);
      console.log(response);
    }
  },
  methods: {
    startPolling() {
      // Clear any existing interval first
      this.stopPolling();
      
      // Set up new polling interval
      this.pollingInterval = setInterval(() => {
        this.fetchAlerts();
      }, this.pollingDelay);
    },
    
    stopPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval);
        this.pollingInterval = null;
      }
    },
    
    async fetchAlerts() {
      try {
        const user_id = this.user.id;
        const response = await axios.get(`/alerts?user_id=${user_id}`);
        this.alerts = response.data;
        // Only show toast when manually refreshing, not during polling
        if (!this.pollingInterval) {
          this.$toast.add({ severity: 'success', summary: 'Success', detail: 'Alerts fetched successfully', life: 3000 });
        }
      } catch (error) {
        console.error('Error fetching alerts:', error);
      }
    },
    async fetchTickers() {
      try {
        const response = await axios.get(`/tickers`);
        this.tickers = response.data;
        console.log(this.tickers);
      } catch (error) {
        console.error('Error fetching tickers:', error);
      }
    },
    validateAlert(alert) {
      if (alert.ticker === "") {
        this.$toast.add({ severity: 'error', summary: 'Error Message', detail: 'Please fill at least the ticker input field', life: 3000 });
        return false;
      }
      return true;
    },
    async createAlert() {
      try {
        if (!this.validateAlert(this.alert)) {
          return;
        }
        const response = await axios.post(`/alert?user_id=${this.user.id}`, this.alert);
        console.log(response.data);
        this.showCreateAlertDialog = false;
        this.alert = {
          ticker: "",
          buy_price: 0,
          tp1: null,
          tp2: null,
          tp3: null,
          box_break: null,
          dip_buy: null,
          sl: null,
          shares: 0,
          percentage_tp: null,
          percentage_sl: null,
          notes: '',
          trailing_stop_percentage: null
        };
        this.fetchAlerts();
        this.$toast.add({ severity: 'success', summary: 'Success Message', detail: 'Alert created successfully', life: 3000 });
      } catch (error) {
        console.error('Error creating alert:', error);
      }
    },
    async updateAlert() {
      if (!this.validateAlert(this.selectedAlert)) {
        return;
      }
      this.selectedAlert.is_sl_hit = false;
      this.selectedAlert.is_tp1_hit = false;
      this.selectedAlert.is_tp2_hit = false;
      this.selectedAlert.is_tp3_hit = false;
      this.selectedAlert.is_dip_buy_hit = false;
      this.selectedAlert.is_box_break_hit = false;
      this.selectedAlert.is_percentage_sl_hit = false;
      this.selectedAlert.is_percentage_tp_hit = false;
      this.selectedAlert.is_trailing_stop_hit = false;
      this.selectedAlert.total_alerts_sent = 0;
      const response = await axios.put(`/alert?user_id=${this.user.id}&alert_id=${this.selectedAlert.id}`, this.selectedAlert);
      this.showUpdateAlertDialog = false;
      console.log(response.data);
      this.$toast.add({ severity: 'success', summary: 'Success Message', detail: 'Alert updated successfully', life: 3000 });
      this.fetchAlerts();
    },
    async deleteAlert(id) {
      const response = await axios.delete(`/alert?user_id=${this.user.id}&alert_id=${id}`);
      this.showDeleteAlertDialog = false;
      console.log(response.data);
      this.$toast.add({ severity: 'success', summary: 'Success Message', detail: 'Alert deleted successfully', life: 3000 });
      this.fetchAlerts();
    },
    async getSelectedTickerInfo(ticker) {
      const response = await axios.get(`/tickers/${ticker}`);
      return response.data;
    },
    logout() {
      // Clear user from localStorage
      localStorage.removeItem('user');
      this.user = null;
      this.stopPolling(); // Stop polling when logging out
      this.$router.push('/login');
    }
  }
}
</script>


<style scoped>
.home-container {
  display: flex;

  min-height: 100vh;
  padding: 1rem;
  background-color: #f5f5f5;
}

.welcome-card {
  width: 100%;
  /* max-width: 600px; */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.title {
  text-align: center;
  margin: 0;
  color: var(--primary-color);
}

.user-info {
  margin-bottom: 2rem;
}

.user-info h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: var(--text-color);
}

.user-info p {
  margin: 0.5rem 0;
}

.alerts-section {
  margin-bottom: 2rem;
}

.alerts-section h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: var(--text-color);
}

.actions {
  display: flex;
  justify-content: center;
}

.positive-change {
  color: #22c55e;
  font-weight: bold;
}

.negative-change {
  color: #ef4444;
  font-weight: bold;
}

.status-indicators {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.sl-hit {
  background-color: #fee2e2;
  color: #b91c1c;
}

.tp-hit {
  background-color: #dcfce7;
  color: #15803d;
}

.box-break {
  background-color: #e0f2fe;
  color: #0369a1;
}
</style>