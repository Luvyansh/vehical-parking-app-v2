<template>
    <NavBar />
    <div class="container mt-5">
        <h2 class="text-center mb-4">Admin Dashboard</h2>
        <h3 class="text-center mb-4">Parking Lots</h3>

        <!-- Top Bar -->
        <div class="d-flex justify-content-between align-items-center mb-3">
            <p class="text-muted mb-0">Available Lots: {{ lots.length }}</p>
            <button class="btn btn-success" @click="showAddModal = true">
                + Add Parking Lot
            </button>
        </div>

        <!-- Lot Cards -->
        <div class="row g-4 mb-4">
            <div class="col-sm-12 col-md-6 col-lg-3" v-for="(lot, index) in displayLots" :key="lot.id">
                <div class="card h-100 shadow-sm d-flex flex-column">
                    <div class="card-header">
                        <h4 class="mb-0 text-truncate">{{ lot.id }}. {{ lot.prime_location_name }}</h4>
                    </div>
                    <div class="card-body">
                        <p class="card-text">Price (per hour): ₹ {{ lot.price }}</p>
                        <p class="card-text">Address: {{ lot.address }}</p>
                        <p class="card-text">Pin Code: {{ lot.pin_code }}</p>
                        <p class="card-text">Number of Spots: {{ lot.number_of_spots }}</p>
                        <p class="card-text">Has Reserved Spots: {{ lot.hasReservedSpots ? 'Yes' : 'No' }}</p>
                    </div>
                    <div class="card-footer mt-auto d-flex justify-content-between">
                        <button class="btn btn-primary btn-sm" @click="openViewModal(lot)">View</button>
                        <button class="btn btn-warning btn-sm" @click="openEditModal(lot)">Edit</button>
                        <!-- inside card-footer -->
                        <button class="btn btn-danger btn-sm" :disabled="lot.hasReservedSpots"
                            @click="deleteLot(lot.id)" data-bs-toggle="tooltip"
                            :title="lot.hasReservedSpots ? 'Cannot delete: reserved spots exist' : ''">
                            Delete
                        </button>
                    </div>
                </div>
            </div>

            <!-- Show All Button -->
            <div v-if="lots.length > 8 && !showAll" class="col-12 d-flex justify-content-center">
                <button class="btn btn-outline-primary" @click="showAll = true">
                    Show All
                </button>
            </div>
        </div>
    </div>

    <!-- All Modals outside layout -->
    <AddLotModal v-if="showAddModal" @close="showAddModal = false" @lot-added="handleLotAdded" />

    <ViewLotModal v-if="showViewModal" :lot="selectedLot" :spots="spots" @close="showViewModal = false" />

    <EditLotModal v-if="showEditModal" :lot="selectedLot" @close="showEditModal = false"
        @lot-updated="handleLotUpdated" />
</template>

<script>
import NavBar from '@/components/NavBar.vue';
import ViewLotModal from '@/components/ViewLotModal.vue';
import EditLotModal from '@/components/EditLotModal.vue';
import AddLotModal from '@/components/AddLotModal.vue';
import * as bootstrap from 'bootstrap';
import { toast } from 'vue3-toastify';

export default {
    name: 'AdminView',
    components: {
        NavBar,
        ViewLotModal,
        EditLotModal,
        AddLotModal
    },
    data() {
        return {
            lots: [],
            spots: [],
            showAll: false,
            showViewModal: false,
            showEditModal: false,
            showAddModal: false,
            selectedLot: null
        };
    },
    computed: {
        displayLots() {
            return this.showAll ? this.lots : this.lots.slice(0, 8);
        }
    },
    async mounted() {
        try {
            const response = await fetch('http://127.0.0.1:5000/admin_dashboard', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                }
            });

            if (!response.ok) {
                toast.error('Access Denied: You are logged in as a user.', { position: 'top-center' });
                this.$router.push('/user_dashboard');
            } else {
                await this.getLots(); // Wait until lots are loaded
                this.enableTooltips(); // Initialize tooltips
            }
        } catch (error) {
            toast.error('Server error.', { position: 'top-center' });
            console.error(error);
        }
    },
    methods: {
        async getLots() {
            try {
                const res = await fetch('http://127.0.0.1:5000/parking_lots', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    }
                });
                const data = await res.json();
                const reservedSpots = data.reservedSpots;
                this.spots = data.spots.map(spot => ({ id: spot.id, lot_id: spot.lot_id, is_available: spot.is_available }));
                const spotIdToLotId = {};
                for (const spot of this.spots) {
                    spotIdToLotId[spot.id] = spot.lot_id;
                }
                const reservedLotIds = new Set();
                for (const reservation of reservedSpots) {
                    const spotId = reservation.spot_id;
                    const lotId = spotIdToLotId[spotId];
                    if (lotId) reservedLotIds.add(lotId);
                }
                this.lots = data.lots.map(lot => ({
                    id: lot.id,
                    prime_location_name: lot.prime_location_name,
                    price: lot.price,
                    address: lot.address,
                    pin_code: lot.pin_code,
                    number_of_spots: lot.number_of_spots,
                    hasReservedSpots: reservedLotIds.has(lot.id)
                }));
            } catch (error) {
                toast.error('Error fetching parking lots.', { position: 'top-center' });
                console.error(error);
            }
        },


        enableTooltips() {
            const tooltipTriggerList = [].slice.call(
                document.querySelectorAll('[data-bs-toggle="tooltip"]')
            );
            tooltipTriggerList.forEach(tooltipTriggerEl => {
                new bootstrap.Tooltip(tooltipTriggerEl);
            });
        },
        openViewModal(lot) {
            this.selectedLot = lot;
            this.showViewModal = true;
        },
        openEditModal(lot) {
            this.selectedLot = lot;
            this.showEditModal = true;
        },
        handleLotAdded() {
            this.showAddModal = false;
            this.getLots();
        },
        handleLotUpdated(updatedLot) {
            this.showEditModal = false;
            const index = this.lots.findIndex(lot => lot.id === updatedLot.id);
            if (index !== -1) {
                this.lots.splice(index, 1, updatedLot);
            }
        },

        async deleteLot(lotId) {
            try {
                const response = await fetch(`http://127.0.0.1:5000/delete_parking_lot/${lotId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    },
                    credentials: 'include'
                });

                if (response.ok) {
                    toast.success('Lot deleted successfully.', { position: 'top-center' });
                    this.getLots();
                } else {
                    toast.error('Failed to delete lot.', { position: 'top-center' });
                }
            } catch (error) {
                toast.error('Server error.', { position: 'top-center' });
                console.error(error);
            }
        }
    }
};
</script>