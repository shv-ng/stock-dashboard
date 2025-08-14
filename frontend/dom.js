
export default {
  cacheElements() {
    return {
      navList: document.getElementById('navList'),
      pageTitle: document.getElementById('pageTitle'),
      pageSubtitle: document.getElementById('pageSubtitle'),
      statsGrid: document.getElementById('statsGrid'),
      chart1Summary: document.getElementById('chart1Summary'),
      chart2Summary: document.getElementById('chart2Summary'),
      hamburger: document.getElementById('hamburger'),
      sidebar: document.getElementById('sidebar'),
      overlay: document.getElementById('overlay')
    };
  },

  renderNavigation(items, onClickItem) {
    const navList = document.getElementById('navList');
    navList.innerHTML = '';

    items.forEach((item, index) => {
      const listItem = document.createElement('li');
      listItem.className = 'nav-item';

      const link = document.createElement('a');
      link.className = 'nav-link';
      link.href = '#';
      link.innerHTML = `<span>${item.name}</span>`;

      link.addEventListener('click', (e) => {
        e.preventDefault();
        onClickItem(index);
        if (window.innerWidth <= 768) {
          this.closeSidebar();
        }
      });

      listItem.appendChild(link);
      navList.appendChild(listItem);
    });
  },

  toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
    document.getElementById('overlay').classList.toggle('show');
  },

  closeSidebar() {
    document.getElementById('sidebar').classList.remove('open');
    document.getElementById('overlay').classList.remove('show');
  },

  handleResponsive() {
    if (window.innerWidth > 768) {
      this.closeSidebar();
    }
  }
};
