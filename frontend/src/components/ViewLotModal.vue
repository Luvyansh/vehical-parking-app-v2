<template>
    <div class="modal fade show d-block" tabindex="-1" role="dialog" style="background-color: rgba(0,0,0,0.5);">
        <div class="modal-dialog modal-dialog-centered" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">View Parking Lot</h5>
                    <button type="button" class="btn-close" @click="$emit('close')"></button>
                </div>
                <div class="modal-body">
                    <p><strong>Name:</strong> {{ lot.prime_location_name }}</p>

                    <hr>
                    <p><strong>Spots Status:</strong></p>
                    <div class="d-flex flex-wrap gap-2 justify-content-center">
                        <div v-for="spot in spots.filter(s => s.lot_id === lot.id)" :key="spot.id"
                            class="free-box rounded d-flex align-items-center justify-content-center"
                            :style="spot.is_available ? 'width: 40px; height: 40px; background-color: lightgreen; border: 1px solid #ccc;' : 'width: 40px; height: 40px; border: 1px solid #333;'"
                            data-bs-toggle="tooltip" data-bs-placement="top" :title="getTooltipContent(spot)"> <img
                                v-if="!spot.is_available" src="@/assets/images/occupied.png" alt="Occupied"
                                style="width: 35px; height: 35px;" />
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" @click="$emit('close')">Close</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import * as bootstrap from 'bootstrap'; // ⭐ ADDED: Import Bootstrap for tooltips ⭐

export default {
    name: 'ViewLotModal',
    props: {
        lot: Object,
        spots: Array,
        // ⭐ ADDED: New prop to receive reservedSpots from parent ⭐
        reservedSpots: {
            type: Array,
            default: () => []
        }
    },
    methods: {
        close() {
            this.$emit('close');
        },
        // ⭐ ADDED: Method to get tooltip content ⭐
        getTooltipContent(spot) {
            if (spot.is_available) {
                return `Spot ID: ${spot.id}\nStatus: Available`;
            } else {
                const reservation = this.reservedSpots.find(res => res.spot_id === spot.id);
                if (reservation) {
                    const formattedParkTime = new Date(reservation.park_time).toLocaleString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: true
                    });
                    // Ensure lot.price is treated as a number before toFixed
                    const lotPriceFormatted = typeof this.lot.price === 'number' ? this.lot.price.toFixed(2) : this.lot.price;

                    return `Spot ID: ${spot.id}\nStatus: Occupied\nReserved by User ID: ${reservation.user_id}\nParked Since: ${formattedParkTime}\nLot Price: ₹${lotPriceFormatted}`;
                }
                return `Spot ID: ${spot.id}\nStatus: Occupied (Details N/A)`; // Fallback if no reservation details found for an occupied spot
            }
        },
        // ⭐ ADDED: Method to initialize Bootstrap Tooltips ⭐
        initializeTooltips() {
            // Destroy any existing tooltips to prevent duplicates on re-render/update
            document.querySelectorAll('.tooltip').forEach(tooltipEl => tooltipEl.remove());

            const tooltipTriggerList = [].slice.call(
                // Query only within the modal's own DOM element
                this.$el.querySelectorAll('[data-bs-toggle="tooltip"]')
            );
            tooltipTriggerList.map(tooltipTriggerEl => {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }
    },
    // ⭐ ADDED: Lifecycle Hooks for Tooltip Management ⭐
    mounted() {
        this.$nextTick(() => { // Ensure DOM is rendered before initializing tooltips
            this.initializeTooltips();
        });
    },
    updated() {
        this.$nextTick(() => { // Re-initialize if spots data changes while modal is open
            this.initializeTooltips();
        });
    },
    beforeUnmount() {
        // Dispose of tooltips to prevent memory leaks when the modal closes
        const tooltipTriggerList = [].slice.call(
            this.$el.querySelectorAll('[data-bs-toggle="tooltip"]')
        );
        tooltipTriggerList.forEach(tooltipTriggerEl => {
            const tooltip = bootstrap.Tooltip.getInstance(tooltipTriggerEl);
            if (tooltip) {
                tooltip.dispose();
            }
        });
    }
};
</script>

<style scoped>
/* ⭐ ADDED: Style to allow newlines in tooltip content ⭐ */
.tooltip-inner {
    white-space: pre-wrap;
    /* Allows for newlines in title attribute */
    text-align: left;
    /* Align text to the left for better readability with newlines */
}

/* Your existing styles below */
.modal {
    background-color: rgba(0, 0, 0, 0.5);
}

.modal-dialog {
    max-width: 800px;
    /* Adjust as needed */
}

.modal-content {
    border-radius: 0.5rem;
}

.free-box {
    /* Existing styles from your template */
    width: 40px;
    height: 40px;
    border: 1px solid #333;
    cursor: pointer;
    /* Indicate it's interactive */
}

/* You had 'free-box rounded d-flex align-items-center justify-content-center' on both,
   I've moved the common styling to .free-box and kept the conditional background/border in the template. */
</style>