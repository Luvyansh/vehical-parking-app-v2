<template>
    <div class="modal-backdrop">
        <div class="modal-container">
            <div class="modal-header">
                <h5 class="modal-title">Select a Spot in {{ lot.prime_location_name }}</h5>
                <button type="button" class="btn-close" @click="$emit('close')"></button>
            </div>

            <div class="modal-body">
                <div class="spot-grid">
                    <div v-for="spot in allSpots" :key="spot.id" class="spot-item">
                        <div v-if="!spot.is_available" class="border border-1 border-dark solid rounded">
                            <img src="@/assets/images/occupied.png" alt="Occupied" class="spot-img" />
                        </div>
                        <button v-else class="btn btn-outline-success" :class="{ selected: selectedSpot === spot.id }"
                            @click="selectSpot(spot.id)" style="width: 100px; height: 100px;">
                            Spot {{ spot.id }}
                        </button>
                    </div>
                </div>
            </div>

            <div class="modal-footer">
                <button class="btn btn-primary" :disabled="!selectedSpot" @click="bookSpot">
                    Book
                </button>
                <button class="btn btn-secondary" @click="$emit('close')">Cancel</button>
            </div>
        </div>
    </div>
</template>

<script>
import { toast } from 'vue3-toastify';
import 'vue3-toastify/dist/index.css';

export default {
    name: 'SpotBookingModal',
    props: {
        lot: Object,
        spots: Array, // only available spots passed
    },
    data() {
        return {
            selectedSpot: null,
            allSpots: [], // includes both available and occupied
        };
    },
    async created() {
        await this.fetchAllSpots();
    },
    methods: {
        async fetchAllSpots() {
            try {
                const res = await fetch(`http://127.0.0.1:5000/get_spots_in_lot/${this.lot.id}`, {
                    method: 'GET',
                    headers: {
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
                    },
                });
                const data = await res.json();
                this.allSpots = data.spots;
            } catch (err) {
                toast.error("Failed to fetch spots.");
            }
        },
        selectSpot(id) {
            this.selectedSpot = this.selectedSpot === id ? null : id;
        },
        async bookSpot() {
            if (!this.selectedSpot) return;
            try {
                const res = await fetch(`http://127.0.0.1:5000/reserve_spot/${this.selectedSpot}`, {
                    method: 'POST',
                    headers: {
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
                        'Content-Type': 'application/json',
                    },
                });
                const data = await res.json();
                toast.success(data.message || "Booking confirmed");
                this.$emit('reserve', this.selectedSpot);
                this.$emit('close');
            } catch (err) {
                toast.error("Failed to reserve spot.");
            }
        },
    },
};
</script>

<style scoped>
.modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1050;
}

.modal-container {
    background: white;
    border-radius: 10px;
    max-width: 600px;
    width: 90%;
    padding: 1rem;
}

.modal-header,
.modal-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-body {
    margin: 1rem 0;
}

.spot-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 1rem;
}

.spot-item {
    text-align: center;
}

.spot-img {
    width: 95px;
    height: 95px;
}

.selected {
    background-color: #198754 !important;
    color: white !important;
}
</style>