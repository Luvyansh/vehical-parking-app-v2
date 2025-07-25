<template>
    <NavBar />
</template>

<script>
    import NavBar from '@/components/NavBar.vue';
    import { toast } from 'vue3-toastify'; // or your toast library

    export default {
        name: 'UserView',
        components: {
            NavBar,
        },
        async mounted() {
            try {
                const response = await fetch('http://127.0.0.1:5000/user_dashboard', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + localStorage.getItem('access_token')
                    },
                    credentials: 'include'
                });

                if (!response.ok) {
                    toast.error('Access Denied: You are logged in as an admin.', { position: 'top-center' });
                    this.$router.push('/admin_dashboard');
                } else if (response.ok) {
                    toast.success('User Authenticated Successfully.', { position: 'top-center' });
                } else {
                    toast.error('Unexpected error occurred.', { position: 'top-center' });
                }
            } catch (error) {
                toast.error('Network error or server unavailable.', { position: 'top-center' });
                console.error(error);
            }
        }
    }
</script>