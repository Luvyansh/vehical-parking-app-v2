<template>
    <div class="modal fade show d-block" tabindex="-1" role="dialog" style="background-color: rgba(0,0,0,0.5);">
        <div class="modal-dialog modal-lg" role="document">
            <div class="modal-content">
                <form @submit.prevent="submitLot">
                    <div class="modal-header">
                        <h5 class="modal-title">Add Parking Lot</h5>
                        <button type="button" class="btn-close" @click="$emit('close')"></button>
                    </div>

                    <div class="modal-body row g-3">
                        <div class="col-md-6">
                            <label class="form-label">Name</label>
                            <input v-model="form.prime_location_name" type="text" class="form-control" required />
                        </div>

                        <div class="col-md-6">
                            <label class="form-label">Select Location</label>
                            <select v-model="form.location_id" class="form-select" required>
                                <option disabled value="">Select a Location</option>
                                <option v-for="loc in locations" :key="loc.id" :value="loc.id">
                                    {{ loc.name }} ({{ loc.city }})
                                </option>
                            </select>
                        </div>

                        <div class="col-md-6">
                            <label class="form-label">Price (per hour)</label>
                            <input v-model="form.price" type="float" class="form-control" required />
                        </div>

                        <div class="col-md-6">
                            <label class="form-label">Number of Spots</label>
                            <input v-model="form.number_of_spots" type="number" class="form-control" required />
                        </div>

                        <div class="col-md-12">
                            <label class="form-label">Address</label>
                            <input v-model="form.address" type="text" class="form-control" required />
                        </div>

                        <div class="col-md-6">
                            <label class="form-label">Pin Code</label>
                            <input v-model="form.pin_code" type="text" class="form-control" required />
                        </div>
                    </div>

                    <div class="modal-footer">
                        <button type="submit" class="btn btn-primary">Add</button>
                        <button type="button" class="btn btn-secondary" @click="$emit('close')">Cancel</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script>
import { toast } from 'vue3-toastify';

export default {
    data() {
        return {
            form: {
                prime_location_name: '',
                price: '',
                address: '',
                pin_code: '',
                number_of_spots: '',
                location_id: ''
            },
            locations: []
        };
    },
    async mounted() {
        try {
            const res = await fetch('http://127.0.0.1:5000/get_locations', {
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: 'Bearer ' + localStorage.getItem('access_token')
                }
            });
            const data = await res.json();
            if (res.ok) {
                this.locations = data.locations;
            } else {
                toast.error(data.message || 'Failed to fetch locations');
            }
        } catch (err) {
            toast.error('Error fetching locations');
        }
    },
    methods: {
        async submitLot() {
            try {
                const response = await fetch('http://127.0.0.1:5000/add_parking_lot', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    },
                    body: JSON.stringify(this.form)
                });

                const result = await response.json();
                if (response.ok) {
                    toast.success(result.message || 'Lot added successfully');
                    this.$emit('lot-added');
                } else {
                    toast.error(result.message || 'Failed to add lot');
                }
            } catch (err) {
                toast.error('Server error');
            }
        }
    }
};
</script>