<template>
    <div class="container mt-5 text-center">
        <h2>User Dashboard</h2>
        <p>{{ userMessage }}</p>
    </div>
</template>

<script>
    import { toast } from 'vue3-toastify';

    export default {
        name: 'UserView',
        data() {
            return {
            userMessage: ''
            };
        },
        async mounted() {
            try {
            const response = await fetch('http://localhost:5000/user_dashboard', {
                method: 'GET',
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include', // 🧠 include session cookie
            });

            const data = await response.json();

            if (!response.ok) {
                toast.error(data.message || 'Access denied', { position: 'top-center' });
                this.$router.push('/login');
            } else {
                this.userMessage = data.message;
                toast.success(data.message, { position: 'top-center' });
            }
            } catch (error) {
            toast.error('Server error while loading user dashboard.', { position: 'top-center' });
            console.error(error);
            }
        }
    };
</script>

<style scoped>
    .container {
        max-width: 600px;
        margin: 0 auto;
    }
</style>