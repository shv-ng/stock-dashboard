import DOM from './dom.js';
import Charts from './charts.js';

const API_URL="http://backend:8000"

class Dashboard {
  constructor() {
    this.items = [];

    this.currentItem = null;
    this.elements = {};
    this.charts = Charts.charts;

    this.init();
  }

  init() {
    this.elements = DOM.cacheElements();
    this.setupEventListeners();
    DOM.renderNavigation(this.items, (index) => this.loadItem(index));
    Charts.initCharts.call(this);

    this.fetchTickers().then(() => {
      this.prefetchAllTickers();
    });
    DOM.handleResponsive();

  }

  setupEventListeners() {
    this.elements.hamburger.addEventListener('click', () => DOM.toggleSidebar());
    this.elements.overlay.addEventListener('click', () => DOM.closeSidebar());
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') DOM.closeSidebar();
    });
    window.addEventListener('resize', () => DOM.handleResponsive());
  }

  // fetch data of clicked item from cache or from backend and update chart
  loadItem(index) {
    const item = this.items[index];
    this.currentItem = item;

    document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
    document.querySelectorAll('.nav-link')[index].classList.add('active');

    this.elements.pageTitle.textContent = item.name;
    this.elements.pageSubtitle.textContent = item.description;

    if (!item.fetched) {
      this.fetchTickerData(index);
    } else {
      Charts.updateCharts.call(this, item);
      this.updateSummaries(item);
    }
  }

  updateSummaries(item) {
    this.elements.chart1Summary.innerHTML = `
<strong>52-Week Low:</strong> ${item.min52.toFixed(4)} | 
<strong>52-Week High:</strong> ${item.max52.toFixed(4)}
`;

    if (item.predictionData) {
      const avgPred = item.predictionData.prices.reduce((a, b) => a + b, 0) / item.predictionData.prices.length;
      this.elements.chart2Summary.innerHTML = `
<strong>Predicted Avg:</strong> ${avgPred.toFixed(4)} | 
<strong>Max Pred:</strong> ${Math.max(...item.predictionData.prices).toFixed(4)}
`;
    }
  }

  // fetch list of all tickers
  async fetchTickers() {
    try {
      const res = await fetch(`${API_URL}/api/list`);
      const tickersData = await res.json();

      this.items = Object.entries(tickersData).map(([symbol, info]) => ({
        symbol,
        name: info.company,
        sector: info.sector,
        chart1: [],
        description: `${info.company} - ${info.sector} - ${symbol}`,
        max52:0,
        min52:0,
        fetched: false 
      }));

      DOM.renderNavigation(this.items, this.loadItem.bind(this));
    } catch (err) {
      console.error('Failed to fetch tickers', err);
    }
  }
  // fetch ticker data from cache or from backend
  async fetchTickerData(index) {
    const item = this.items[index];
    if (item.fetched) return; 

    try {
      const res = await fetch(`${API_URL}/api/history/${item.symbol}`);
      const data = await res.json();

      // Extract chart1 data from API
      item.chartData = {
        dates: data.data.map(row => row.Date),
        open: data.data.map(row => row.Open),
        high: data.data.map(row => row.High),
        low: data.data.map(row => row.Low),
        close: data.data.map(row => row.Close),
      };
      item.fetched = true;
      item.min52=data.min52;
      item.max52=data.max52;

      // If user is currently viewing this item, update charts immediately
      if (this.currentItem === item) {
        Charts.updateCharts.call(this, item);
        this.updateSummaries(item);
      }
    } catch (err) {
      console.error(`Failed to fetch data for ${item.symbol}`, err);
    }
    // Fetch predictions
    try {
      const predRes = await fetch(`${API_URL}/api/predict/${item.symbol}`);
      const predData = await predRes.json();
      item.predictionData = {
        dates: predData.predictions.map(p => p.date),
        prices: predData.predictions.map(p => p.predicted_price)
      };
    } catch (err) {
      console.error(`Failed to fetch prediction for ${item.symbol}`, err);
    }
  }
  // bg fetching all ticker data
  prefetchAllTickers() {
    let delay = 0;
    this.items.forEach((_, index) => {
      setTimeout(() => {
        this.fetchTickerData(index);
      }, delay);
      delay += 300; 
    });
  };
}

document.addEventListener('DOMContentLoaded', () => {
  new Dashboard();
});
