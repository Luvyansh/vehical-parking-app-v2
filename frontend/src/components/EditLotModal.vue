<template>
    <div class="modal fade show d-block" tabindex="-1" aria-labelledby="editLotModalLabel" aria-hidden="true"
        style="background-color: rgba(0, 0, 0, 0.5);">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="editLotModalLabel">Edit Parking Lot (ID: {{ editedLot.id }})</h5>
                    <button type="button" class="btn-close" @click="$emit('close')" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="submitEdit">
                        <div class="mb-3">
                            <label for="primeLocationName" class="form-label">Prime Location Name</label>
                            <input type="text" class="form-control" id="primeLocationName"
                                v-model="editedLot.prime_location_name" required>
                        </div>
                        <div class="mb-3">
                            <label for="price" class="form-label">Price (per hour)</label>
                            <input type="float" class="form-control" id="price" v-model.number="editedLot.price"
                                required min="0">
                        </div>
                        <div class="mb-3">
                            <label for="address" class="form-label">Address</label>
                            <input type="text" class="form-control" id="address" v-model="editedLot.address" required>
                        </div>
                        <div class="mb-3">
                            <label for="pinCode" class="form-label">Pin Code</label>
                            <input type="text" class="form-control" id="pinCode" v-model="editedLot.pin_code" required
                                pattern="[0-9]{6}" title="Pin code must be 6 digits">
                        </div>
                        <div class="mb-3">
                            <label for="numberOfSpots" class="form-label">Number of Spots</label>
                            <input type="number" class="form-control" id="numberOfSpots"
                                v-model.number="editedLot.number_of_spots" required min="1">
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" @click="$emit('close')">Close</button>
                            <button type="submit" class="btn btn-primary">Save Changes</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { toast } from 'vue3-toastify';

export default {
    name: 'EditLotModal',
    props: {
        lot: {
            type: Object,
            required: true
        }
    },
    data() {
        return {
            editedLot: { ...this.lot } // Create a copy to avoid directly mutating the prop
        };
    },
    methods: {
        async submitEdit() {
            try {
                const response = await fetch(`http://127.0.0.1:5000/update_parking_lot/${this.editedLot.id}`, {
                    method: 'POST', // Your backend uses POST for update
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    },
                    body: JSON.stringify({
                        prime_location_name: this.editedLot.prime_location_name,
                        price: this.editedLot.price,
                        address: this.editedLot.address,
                        pin_code: this.editedLot.pin_code,
                        number_of_spots: this.editedLot.number_of_spots,
                    })
                });

                if (response.ok) {
                    toast.success('Parking lot updated successfully!', { position: 'top-center' });
                    this.$emit('lot-updated', this.editedLot); // Emit event to notify parent
                } else {
                    const errorData = await response.json();
                    toast.error(errorData.message || 'Failed to update parking lot.', { position: 'top-center' });
                }
            } catch (error) {
                toast.error('Server error during update.', { position: 'top-center' });
                console.error('Error updating parking lot:', error);
            }
        }
    }
};
</script>

<style scoped>
/* Add any specific styles for your modal here if needed */
</style>