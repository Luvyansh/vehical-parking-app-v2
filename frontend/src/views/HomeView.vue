<template>
  <NavBar />
  <div class="home">
    <!-- Hero Section -->
    <section
      class="hero-section d-flex flex-column justify-content-center align-items-center text-white text-center py-5">
      <h1 class="display-3 fw-bold animate__animated animate__fadeInDown">Find Your Perfect Parking Spot</h1>
      <p class="lead mt-3 animate__animated animate__fadeInUp animate__delay-1s">
        Seamlessly discover and book parking lots near you.
      </p>
      <router-link to="/login" class="btn btn-primary btn-lg mt-4 animate__animated animate__zoomIn animate__delay-2s">
        Explore Parking
      </router-link>
    </section>

    <!-- Locations Marquee Section -->
    <section class="locations-section py-5 bg-light">
      <h2 class="text-center mb-4 fw-bold animate__animated animate__fadeIn">Available Locations</h2>
      <div class="vertical-marquee-container animate__animated animate__fadeInUp animate__delay-1s">
        <div class="vertical-marquee">
          <div class="vertical-marquee__inner" :style="{ animationDuration: marqueeSpeed }">
            <div class="vertical-marquee__group" v-for="(group, index) in [1, 2]" :key="index">
              <div v-for="location in locations" :key="location.id" class="location-card shadow-sm">
                <h5 class="card-title mb-1">{{ location.name }}</h5>
                <p class="card-text text-muted">{{ location.city }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="isLoadingLocations" class="text-center mt-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading locations...</span>
        </div>
        <p class="text-muted mt-2">Loading locations...</p>
      </div>
      <div v-else-if="!locations.length" class="text-center mt-4 text-muted">
        No locations available at the moment.
      </div>
    </section>

    <!-- Placeholder for other sections (e.g., features, testimonials) -->
    <section class="features-section py-5 text-center">
      <h2 class="fw-bold mb-4">Why Choose Us?</h2>
      <div class="row justify-content-center">
        <div class="col-md-4 mb-4">
          <div class="feature-card p-4 shadow-sm rounded">
            <i class="bi bi-geo-alt-fill feature-icon mb-3"></i>
            <h4>Easy Location</h4>
            <p>Find parking spots effortlessly with our intuitive search.</p>
          </div>
        </div>
        <div class="col-md-4 mb-4">
          <div class="feature-card p-4 shadow-sm rounded">
            <i class="bi bi-calendar-check-fill feature-icon mb-3"></i>
            <h4>Instant Booking</h4>
            <p>Book your spot in advance and save time.</p>
          </div>
        </div>
        <div class="col-md-4 mb-4">
          <div class="feature-card p-4 shadow-sm rounded">
            <i class="bi bi-currency-dollar feature-icon mb-3"></i>
            <h4>Transparent Pricing</h4>
            <p>No hidden fees, just clear and fair rates.</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';
import userMixin from '@/mixins/userMixin';
import { toast } from 'vue3-toastify';
// CSS imports are now in the <style> block

export default {
  name: 'HomeView',
  mixins: [userMixin],
  components: {
    NavBar
  },
  data() {
    return {
      locations: [],
      isLoadingLocations: false,
      // Calculate marquee speed dynamically based on number of locations
      // Each location card will contribute to the total height to scroll
      marqueeBaseSpeed: 15, // seconds for a small number of items
      marqueeSpeedFactor: 0.5 // Adjust this to make it faster/slower with more items
    };
  },
  computed: {
    marqueeSpeed() {
      // Adjust speed based on the actual number of locations
      // More locations means a longer scroll, so we increase the duration
      if (this.locations.length === 0) return '0s';
      const calculatedSpeed = this.marqueeBaseSpeed + (this.locations.length * this.marqueeSpeedFactor);
      return `${calculatedSpeed}s`;
    }
  },
  async mounted() {
    await this.fetchLocations();
  },
  methods: {
    /**
     * Fetches location data from the backend.
     */
    async fetchLocations() {
      this.isLoadingLocations = true;
      try {
        const response = await fetch('http://127.0.0.1:5000/get_locations', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            // Assuming get_locations does not require authentication
            // If it does, uncomment the line below:
            // 'Authorization': 'Bearer ' + localStorage.getItem('access_token')
          },
        });

        if (response.ok) {
          const data = await response.json();
          this.locations = data.locations;
        } else {
          const errorData = await response.json();
          toast.error(errorData.message || 'Failed to fetch locations.', { position: 'top-center' });
        }
      } catch (error) {
        console.error('Error fetching locations:', error);
        toast.error('Server error while fetching locations.', { position: 'top-center' });
      } finally {
        this.isLoadingLocations = false;
      }
    }
  }
}
</script>

<style scoped>
/* ⭐ MODIFIED: Corrected import path for bootstrap-icons ⭐ */
@import 'animate.css';
@import 'bootstrap-icons/font/bootstrap-icons.css';
/* Changed from font/bootstrap-icons.css */

/* Hero Section Styling */
.hero-section {
  background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url('https://placehold.co/1920x1080/007bff/ffffff?text=Parking+PAL') center center no-repeat;
  background-size: cover;
  min-height: 60vh;
  /* Adjust height as needed */
  padding: 80px 20px;
  position: relative;
  overflow: hidden;
  /* Ensure no overflow from animations */
}

.hero-section h1,
.hero-section p {
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

.hero-section .btn-primary {
  background-color: #28a745;
  border-color: #28a745;
  transition: background-color 0.3s ease, transform 0.3s ease;
}

.hero-section .btn-primary:hover {
  background-color: #218838;
  transform: translateY(-3px);
}

/* Vertical Marquee Styling */
.locations-section {
  background-color: #f8f9fa;
  padding: 50px 0;
}

.vertical-marquee-container {
  height: 300px;
  /* Fixed height for the marquee display area */
  overflow: hidden;
  position: relative;
  margin: 0 auto;
  max-width: 90%;
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  background-color: #ffffff;
  /* Add a background to the container */
  -webkit-mask-image: linear-gradient(to bottom,
      transparent 0%,
      black 10%,
      black 90%,
      transparent 100%);
  mask-image: linear-gradient(to bottom,
      transparent 0%,
      black 10%,
      black 90%,
      transparent 100%);
}

.vertical-marquee {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.vertical-marquee__inner {
  display: flex;
  flex-direction: column;
  width: 100%;
  /* Ensure inner takes full width */
  animation: vertical-marquee linear infinite;
  /* animation-duration set via Vue computed property */
}

.vertical-marquee__group {
  display: flex;
  flex-direction: column;
  /* Stack cards vertically within the group */
  align-items: center;
  /* Center cards horizontally within the group */
}

.location-card {
  background: #007bff;
  /* Primary color for cards */
  color: white;
  padding: 15px 20px;
  margin: 10px 0;
  /* Vertical margin between cards */
  border-radius: 10px;
  text-align: center;
  width: 90%;
  /* Make cards take most of the width */
  max-width: 300px;
  /* Max width for individual cards */
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.location-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.location-card h5 {
  font-size: 1.25rem;
  margin-bottom: 5px;
}

.location-card p {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
}


@keyframes vertical-marquee {
  0% {
    transform: translateY(0);
  }

  100% {
    transform: translateY(-50%);
  }
}

/* Features Section Styling */
.features-section {
  background-color: #ffffff;
}

.feature-card {
  background-color: #f0f8ff;
  /* Light blue background */
  border: 1px solid #e0eaf6;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 3rem;
  color: #007bff;
}
</style>