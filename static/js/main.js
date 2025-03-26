// Mobile Menu Toggle
document.addEventListener("DOMContentLoaded", () => {
    const mobileMenuBtn = document.querySelector(".mobile-menu-btn")
    const nav = document.querySelector("nav")
  
    if (mobileMenuBtn) {
      mobileMenuBtn.addEventListener("click", function () {
        nav.classList.toggle("active")
  
        // Toggle icon
        const icon = this.querySelector("i")
        if (icon.classList.contains("fa-bars")) {
          icon.classList.remove("fa-bars")
          icon.classList.add("fa-times")
        } else {
          icon.classList.remove("fa-times")
          icon.classList.add("fa-bars")
        }
      })
    }
  
    // Close mobile menu when clicking outside
    document.addEventListener("click", (event) => {
      if (
        nav &&
        nav.classList.contains("active") &&
        !nav.contains(event.target) &&
        !mobileMenuBtn.contains(event.target)
      ) {
        nav.classList.remove("active")
        const icon = mobileMenuBtn.querySelector("i")
        icon.classList.remove("fa-times")
        icon.classList.add("fa-bars")
      }
    })
  
    // Tab functionality
    const tabBtns = document.querySelectorAll(".tab-btn")
    const tabContents = document.querySelectorAll(".tab-content")
  
    if (tabBtns.length > 0) {
      tabBtns.forEach((btn) => {
        btn.addEventListener("click", function () {
          // Remove active class from all buttons and contents
          tabBtns.forEach((btn) => btn.classList.remove("active"))
          tabContents.forEach((content) => content.classList.remove("active"))
  
          // Add active class to clicked button and corresponding content
          this.classList.add("active")
          const tabId = this.getAttribute("data-tab")
          document.getElementById(tabId).classList.add("active")
        })
      })
    }
  
    // Format currency
    window.formatCurrency = (amount) =>
      new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
      }).format(amount)
  
    // Format date
    window.formatDate = (dateString) => {
      const options = { year: "numeric", month: "long", day: "numeric" }
      return new Date(dateString).toLocaleDateString("en-US", options)
    }
  
    // Format time
    window.formatTime = (timeString) => {
      const options = { hour: "numeric", minute: "2-digit", hour12: true }
      return new Date(`2000-01-01T${timeString}`).toLocaleTimeString("en-US", options)
    }
  
    // Generate star rating HTML
    window.generateStarRating = (rating) => {
      let starsHtml = ""
      const fullStars = Math.floor(rating)
      const halfStar = rating % 1 >= 0.5
      const emptyStars = 5 - fullStars - (halfStar ? 1 : 0)
  
      for (let i = 0; i < fullStars; i++) {
        starsHtml += '<i class="fas fa-star"></i>'
      }
  
      if (halfStar) {
        starsHtml += '<i class="fas fa-star-half-alt"></i>'
      }
  
      for (let i = 0; i < emptyStars; i++) {
        starsHtml += '<i class="far fa-star"></i>'
      }
  
      return starsHtml
    }
  
    // API base URL
    window.apiBaseUrl = "http://127.0.0.1:8000/go/api/"
  })
  
  