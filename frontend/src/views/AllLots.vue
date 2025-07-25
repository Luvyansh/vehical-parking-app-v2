<template>
    <NavBar />
    <div class="container mt-5">
        <h2 class="text-center mb-4">All Parking Lots</h2>
        <router-link to="/create_lot" class="btn btn-outline-primary">Create Parking Lot</router-link>

        <div class="card mb-4 shadow-sm" v-for="lot in lots" :key="lot.id">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">Location: {{ lot.prime_location_name }}</h5>
                <router-link :to="`/update_parking_lot/${lot.id}`" class="btn btn-warning btn-sm me-2">Edit</router-link>
                <button class="btn btn-danger btn-sm" @click="deleteLot(lot.id)">Delete</button>
            </div>
            <div class="card-body">
                <p class="card-text">Price: ₹ {{ lot.price }}</p>
                <p class="card-text">Address: {{ lot.address }}</p>
                <p class="card-text">Pin Code: {{ lot.pin_code }}</p>
                <p class="card-text">Number of Spots: {{ lot.number_of_spots }}</p>
            </div>
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
                lots: '',
            };
        },
        async created() {
            await this.getLots();
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
                    this.lots = data.lots;
                } catch (err) {
                    toast.error(data.message);
                }
            },
            async deleteLot(id) {
                if (!confirm('Are you sure?')) return;
                try {
                    const res = await fetch(`http://127.0.0.1:5000/delete_parking_lot/${id}`, {
                        method: 'DELETE',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                        }
                    });
                    const data = await res.json();
                    toast.success(data.message);
                    this.getLots();
                } catch (err) {
                    toast.error('Failed to delete lot');
                }
            },
        },
    }
</script>