class LGallery {
  items;
  lightGallery;
  element;
  index = PER_PAGE;

  /**
   * Create a lightGallery instance and populate it with the first page of gallery items
   */
  init (params = {}) {
    // Create the lightGallery instance
    this.element = document.getElementById('lightgallery');
    this.lightGallery = lightGallery(this.element, Object.assign({
      plugins: [lgZoom, lgThumbnail, lgVideo, lgFullscreen, lgAutoplay, lgRotate],
      speed: 500,
      /*
      This license key was graciously provided by LightGallery under their
      GPLv3 open-source project license:
      */
      licenseKey: '0000-0000-000-0000'
    }, params.lgConfig));
    this.items = params.items;

    let timeout
    window.addEventListener('scroll', () => {
      if (timeout) clearTimeout(timeout);
      timeout = setTimeout(lgallery.handleScroll, 1000);
    });
    lgallery.handleScroll();
  }

  /**
   * Listen for scroll events and load more gallery items
   */
  handleScroll () {
    const rect = lgallery.element.getBoundingClientRect();
    const scrollPosition = Math.max(0, rect.bottom - window.innerHeight);
    const buffer = 200 // pixels before bottom to trigger load

    if (scrollPosition <= buffer) {
      lgallery.loadMoreItems();
    }
  }

  /**
   * Load more gallery items as per lightGallery docs
   * https://www.lightgalleryjs.com/demos/infinite-scrolling/
   */
  loadMoreItems () {
    if (this.index < this.items.length) {
      // Append new thumbnails
      this.items
        .slice(this.index, this.index + PER_PAGE)
        .forEach(item => {
          this.element.insertAdjacentHTML('beforeend', item.html + '\n');
        })
      this.index += PER_PAGE;
      this.lightGallery.refresh();
    } else {
      // Remove the loading spinner once all items are loaded
      document.getElementById('loading-spinner')?.remove();
    }
  }
}
const lgallery = new LGallery();