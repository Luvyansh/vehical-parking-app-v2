<template>
    <div class="container mt-5">
        <h2 class="text-center mb-4">Register</h2>
        <div class="home-form bg-light p-4 rounded shadow">
            <form @submit.prevent="register">
                <div class="form-group mb-3">
                    <label for="name">Full Name</label>
                    <input type="text" v-model="name" class="form-control" id="name" placeholder="Enter name" required>
                </div>
                <div class="form-group mb-3">
                    <label for="username">Username</label>
                    <input type="text" v-model="username" class="form-control" id="username" placeholder="Enter username" required>
                </div>
                <div class="form-group mb-3">
                    <label for="email">Email</label>
                    <input type="email" v-model="email" class="form-control" id="email" placeholder="Enter email" required>
                </div>
                <div class="form-group mb-3">
                    <label for="password">Password</label>
                    <input type="password" v-model="password" class="form-control" id="password" placeholder="Enter password" required>
                </div>
                <div class="form-group mb-3">
                    <label for="confirmPassword">Confirm Password</label>
                    <input type="password" v-model="confirmPassword" class="form-control" id="confirmPassword" placeholder="Confirm password" required>
                </div>
                <button type="submit" class="btn btn-primary">Register</button>
            </form>
        </div>
    </div>
</template>

<script>
    import { toast } from 'vue3-toastify';

    export default {
        data() {
            return {
            name: '',
            username: '',
            email: '',
            password: '',
            confirmPassword: '',
            };
        },
        methods: {
            checkPasswordsMatch() {
            return this.password === this.confirmPassword;
            },
            async register() {
            if (!this.checkPasswordsMatch()) {
                toast.error('Passwords do not match');
                return;
            }

            try {
                const response = await fetch('http://127.0.0.1:5000/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: this.name,
                    username: this.username,
                    email: this.email,
                    password: this.password,
                }),
                });

                const data = await response.json();

                if (!response.ok) {
                if (data.message === "User already exists") {
                    toast.warning(data.message, {
                    onClose: () => {
                        this.$router.push('/login');
                    },
                });
                } else {
                    toast.error(data.message || "Registration failed");
                }
                } else {
                toast.success(data.message || "Registration successful", {
                    onClose: () => {
                    this.$router.push('/login');
                    },
                });
                }
            } catch (error) {
                toast.error("Server error. Try again later.");
            }
            }
        }
    }
</script>


<style scoped>
.home-form {
    max-width: 400px;
    margin: 0 auto;
}
</style>