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
                            :title="'Spot ID: ' + spot.id">
                            <div v-if="!spot.is_available"
                                class="free-box rounded d-flex align-items-center justify-content-center"
                                style="width: 40px; height: 40px; border: 1px solid #333;">
                                <img src="@/assets/images/occupied.png" alt="Occupied"
                                    style="width: 35px; height: 35px;" />
                            </div>
                            <div v-else class="free-box"
                                style="width: 40px; height: 40px; background-color: lightgreen; border: 1px solid #ccc;">
                            </div>
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
export default {
    name: 'ViewLotModal',
    props: {
        lot: Object,
        spots: Array
    },
    methods: {
        close() {
            this.$emit('close');
        },
    },
};
</script>