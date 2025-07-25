<template>
    <NavBar />
    <div class="container mt-5">
        <h2 class="text-center mb-4">Create Parking Lot</h2>
        <div class="add-form bg-light p-4 rounded shadow">
            <form @submit.prevent="createLot">
                <div class="form-group mb-3">
                    <label for="prime_location_name">Prime Location Name</label>
                    <input type="text" v-model="prime_location_name" class="form-control" id="prime_location_name" placeholder="Enter Location Name" required>
                </div>
                <div class="form-group mb-3">
                    <label for="price">Price</label>
                    <input type="number" v-model="price" class="form-control" id="price" placeholder="Price per Hour" required>
                </div>
                <div class="form-group mb-3">
                    <label for="address">Address</label>
                    <input type="text" v-model="address" class="form-control" id="address" placeholder="Enter address" required>
                </div>
                <div class="form-group mb-3">
                    <label for="pin_code">Pin Code</label>
                    <input type="text" v-model="pin_code" class="form-control" id="pin_code" placeholder="Enter pin code" required>
                </div>
                <div class="form-group mb-3">
                    <label for="number_of_spots">Number of Spots</label>
                    <input type="number" v-model="number_of_spots" class="form-control" id="number_of_spots" placeholder="Enter number of spots" required>
                </div>
                <button type="submit" class="btn btn-primary">Create</button>
            </form>
        </div>
    </div>
</template>

<script>
    import NavBar from '@/components/NavBar.vue';
    export default {
        data() {
            return {
                lot: {
                    prime_location_name: '',
                    price: '',
                    address: '',
                    pin_code: '',
                    number_of_spots: ''
                }
            }
        },
        components: {
            NavBar,
        },
        methods: {
            async createLot() {
                const response = await fetch('http://127.0.0.1:5000/add_parking_lot', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    },
                    body: JSON.stringify(this.lot)
                })
                data = await response.json()
                if (!response.ok) {
                    toast.error(data.message, { position: 'top-center' })
                } else {
                    toast.success(data.message, { position: 'top-center' })
                    if (data.redirect) {
                        this.$router.push('/all_lots')
                }
                }
            }
        }
    }
</script>