
export default {
  charts: {},

  initCharts() {
    const commonOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: { font: { size: 12 }, padding: 20 }
        }
      },
      scales: {
        y: { beginAtZero: true, grid: { color: '#f3f4f6' }, ticks: { font: { size: 11 } } },
        x: { grid: { display: false }, ticks: { font: { size: 11 } } }
      }
    };

    // Chart 1
    this.charts.chart1 = new Chart(document.getElementById('chart1'), {
      type: 'line',
      data: {
        labels: [],
      },
      options: {
        ...commonOptions,
        plugins: {
          ...commonOptions.plugins,
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: 'white',
            bodyColor: 'white',
            borderColor: 'rgb(99, 102, 241)',
            borderWidth: 0.1
          }
        }
      }
    });

    // Chart 2 - commented out
    /*
    this.charts.chart2 = new Chart(document.getElementById('chart2'), {...});
    */
  },

updateCharts(item) {
  const data = item.chartData;
  this.charts.chart1.data.labels = data.dates;
  this.charts.chart1.data.datasets = [
    {
      label: 'High',
      data: data.high,
      borderColor: 'rgb(16, 185, 129)',
      backgroundColor: 'rgba(16, 185, 129, 0.2)',
      tension: 0.3,
      fill: '+1', // Fill to the next dataset (Low)
      pointRadius: 0,
      pointHoverRadius: 0,
      order: 1
    },
    {
      label: 'Low',
      data: data.low,
      borderColor: 'rgb(239, 68, 68)',
      backgroundColor: 'rgba(239, 68, 68, 0.1)',
      tension: 0.3,
      fill: false,
      pointRadius: 0,
      pointHoverRadius: 0,
      order: 2
    },
  ];
  this.charts.chart1.update('active');
}
};
