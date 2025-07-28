<template>
    <NavBar />
    <div class="container py-5">
        <div class="text-center mb-5">
            <h2 class="fw-bold">Parking Lots</h2>
        </div>

        <!-- Animated Card Group -->
        <transition-group name="fade" tag="div" class="row" appear>
            <div v-for="lot in visibleLots" :key="lot.id" class="col-12 col-md-6 col-lg-4 mb-4">
                <div class="card shadow border-0 h-100">
                    <div class="card-header bg-primary text-white text-center">
                        <h5 class="mb-0">{{ lot.prime_location_name }}</h5>
                    </div>
                    <div class="card-body">
                        <p><strong>Address:</strong> {{ lot.address }}</p>
                        <p><strong>Price:</strong> ₹{{ lot.price }} / hr</p>
                        <p>
                            <strong>Available Spots:</strong>
                            {{
                                spots.filter(
                                    (spot) => spot.lot_id === lot.id && spot.is_available
                                ).length
                            }}
                        </p>
                    </div>
                    <div class="card-footer text-center">
                        <button class="btn btn-outline-primary" @click="openModal(lot)">
                            View / Book
                        </button>
                    </div>
                </div>
            </div>
        </transition-group>

        <!-- Show More Button -->
        <div v-if="lots.length > 6 && !showAll" class="text-center mt-3">
            <button class="btn btn-secondary" @click="showAll = true">
                Show More
            </button>
        </div>

        <!-- Modal -->
        <SpotBookingModal v-if="selectedLot" :lot="selectedLot"
            :spots="spots.filter((s) => s.lot_id === selectedLot.id && s.is_available)" @close="selectedLot = null"
            @reserve="handleSpotReserved" /> <!-- Changed @reserve to call handleSpotReserved -->
    </div>
</template>

<script>
import SpotBookingModal from '@/components/SpotBookingModal.vue';
import NavBar from '@/components/NavBar.vue';
import { toast } from 'vue3-toastify';

export default {
    name: 'BookingView',
    components: {
        NavBar,
        SpotBookingModal,
    },
    data() {
        return {
            lots: [],
            spots: [],
            locations: [],
            selectedLot: null,
            showAll: false,
        };
    },
    computed: {
        visibleLots() {
            return this.showAll ? this.lots : this.lots.slice(0, 6);
        },
    },
    async mounted() {
        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                this.$router.push('/login');
                return;
            }

            const response = await fetch('http://127.0.0.1:5000/user_dashboard', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
            });
            if (!response.ok) {
                this.$router.push('/login');
                return;
            }
        } catch (error) {
            toast.error('Server error.', { position: 'top-center' });
            console.error(error);
            this.$router.push('/login');
            return;
        }
        await this.getLots();
        await this.getLocations();
    },
    methods: {
        async getLots() {
            try {
                const res = await fetch('http://127.0.0.1:5000/get_lots', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
                    },
                });
                const data = await res.json();
                this.lots = data.lots;
                this.spots = data.spots;
            } catch (err) {
                toast.error('Failed to fetch lots.');
            }
        },
        async getLocations() {
            try {
                const res = await fetch('http://127.0.0.1:5000/get_locations', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
                    },
                });
                const data = await res.json();
                this.locations = data.locations;
            } catch (err) {
                toast.error('Failed to fetch locations.');
            }
        },
        // This method is now responsible for refreshing data after the modal books a spot
        async handleSpotReserved() {
            // Close the modal
            this.selectedLot = null;
            // Refresh the lots and spots data to reflect the change in availability
            await this.getLots();
        },
        openModal(lot) {
            this.selectedLot = lot;
        },
    },
};
</script>

<style scoped>
/* Add your existing styles here */
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

/* ⭐ MISSING CLASS ⭐ */
.fade-move {
    transition: transform 0.5s ease;
    /* Adjust duration and easing as needed */
}

.container {
    max-width: 1200px;
}

.card {
    border-radius: 15px;
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.card-header {
    border-top-left-radius: 15px;
    border-top-right-radius: 15px;
    padding: 1rem;
}

.card-body p {
    margin-bottom: 0.5rem;
}

.card-footer {
    background-color: #f8f9fa;
    border-bottom-left-radius: 15px;
    border-bottom-right-radius: 15px;
    padding: 1rem;
}

.btn-outline-primary {
    border-color: #007bff;
    color: #007bff;
}

.btn-outline-primary:hover {
    background-color: #007bff;
    color: white;
}
</style>