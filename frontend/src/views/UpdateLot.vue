<template>
    <NavBar />
    <div class="container mt-5">
        <h2 class="text-center mb-4">Update Parking Lot</h2>
        <div class="add-form bg-light p-4 rounded shadow">
            <form @submit.prevent="updateLot">
                <div class="form-group mb-3">
                    <label for="prime_location_name">Prime Location Name</label>
                    <input type="text" class="form-control" id="prime_location_name" placeholder="Enter Location Name" required>
                </div>
                <div class="form-group mb-3">
                    <label for="price">Price</label>
                    <input type="number" class="form-control" id="price" placeholder="Price per Hour" required>
                </div>
                <div class="form-group mb-3">
                    <label for="address">Address</label>
                    <input type="text" class="form-control" id="address" placeholder="Enter address" required>
                </div>
                <div class="form-group mb-3">
                    <label for="pin_code">Pin Code</label>
                    <input type="text" class="form-control" id="pin_code" placeholder="Enter pin code" required>
                </div>
                <div class="form-group mb-3">
                    <label for="number_of_spots">Number of Spots</label>
                    <input type="number" class="form-control" id="number_of_spots" placeholder="Enter number of spots" required>
                </div>
                <button type="submit" class="btn btn-primary">Create</button>
            </form>
        </div>
    </div>
</template>

<script>
    import NavBar from '@/components/NavBar.vue';
    export default {
        name: 'AllLots',
        components: {
            NavBar,
        },
        data() {
            return {
                lot: [],
            };
        },
    }
</script>