<template>
    <NavBar />
    <div class="container d-flex flex-column align-items-center justify-content-center mt-5">
        <h2 class="mb-4 text-center">View / Update Profile</h2>

        <div class="card shadow-sm p-4 w-100" style="max-width: 500px;">
            <form @submit.prevent="updateProfile">
                <div class="mb-3">
                    <label for="name" class="form-label">Name</label>
                    <input type="text" id="name" v-model.trim="user.name" class="form-control"
                        :class="{ 'is-invalid': errors.name }" />
                    <div class="invalid-feedback" v-if="errors.name">{{ errors.name }}</div>
                </div>

                <div class="mb-3">
                    <label for="username" class="form-label">Username</label>
                    <input type="text" id="username" v-model.trim="user.username" class="form-control"
                        :class="{ 'is-invalid': errors.username }" />
                    <div class="invalid-feedback" v-if="errors.username">{{ errors.username }}</div>
                </div>

                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" id="email" v-model.trim="user.email" class="form-control"
                        :class="{ 'is-invalid': errors.email }" />
                    <div class="invalid-feedback" v-if="errors.email">{{ errors.email }}</div>
                </div>

                <button type="submit" class="btn btn-primary w-100 mt-3" :disabled="isLoading">
                    <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status"
                        aria-hidden="true"></span>
                    <span v-else>Save Changes</span>
                </button>
            </form>
        </div>
    </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue';
import { toast } from 'vue3-toastify';

export default {
    name: 'ProfileView',
    components: {
        NavBar,
    },
    data() {
        return {
            user: {
                name: '',
                username: '',
                email: '',
            },
            originalUsername: '', // To store the username fetched initially for uniqueness check
            availableUsernames: [], // List of all usernames for uniqueness validation
            errors: {
                name: '',
                username: '',
                email: '',
            },
            isLoading: false,
        };
    },
    async mounted() {
        // Fetch user profile and all usernames when the component is mounted
        await this.fetchUserProfile();
        await this.fetchUsernames();
    },
    methods: {
        /**
         * Fetches the current user's profile information from the backend.
         * Populates the form fields and stores the original username.
         */
        async fetchUserProfile() {
            try {
                const token = localStorage.getItem('access_token');
                if (!token) {
                    this.$router.push('/login');
                    toast.error('Authentication required.', { position: 'top-center' });
                    return;
                }

                const response = await fetch('http://127.0.0.1:5000/user_profile', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    this.user.name = data.name;
                    this.user.username = data.username;
                    this.user.email = data.email;
                    this.originalUsername = data.username; // Store original username
                } else {
                    const errorData = await response.json();
                    toast.error(errorData.message || 'Failed to fetch user profile.', { position: 'top-center' });
                    if (response.status === 401) {
                        this.$router.push('/login');
                    }
                }
            } catch (error) {
                console.error('Error fetching user profile:', error);
                toast.error('Server error while fetching profile.', { position: 'top-center' });
            }
        },

        /**
         * Fetches all existing usernames from the backend for uniqueness validation.
         */
        async fetchUsernames() {
            try {
                const token = localStorage.getItem('access_token');
                if (!token) {
                    // Already handled in fetchUserProfile, but good to have a check
                    return;
                }

                const response = await fetch('http://127.0.0.1:5000/get_usernames', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    this.availableUsernames = data.usernames;
                } else {
                    const errorData = await response.json();
                    toast.error(errorData.message || 'Failed to fetch usernames.', { position: 'top-center' });
                }
            } catch (error) {
                console.error('Error fetching usernames:', error);
                toast.error('Server error while fetching usernames.', { position: 'top-center' });
            }
        },

        /**
         * Performs client-side validation for the form fields.
         * @returns {boolean} True if the form is valid, false otherwise.
         */
        validateForm() {
            this.errors = { name: '', username: '', email: '' }; // Clear previous errors
            let isValid = true;

            // Name validation
            if (!this.user.name) {
                this.errors.name = 'Name is required.';
                isValid = false;
            }

            // Username validation
            if (!this.user.username) {
                this.errors.username = 'Username is required.';
                isValid = false;
            } else if (this.user.username.length < 3) {
                this.errors.username = 'Username must be at least 3 characters long.';
                isValid = false;
            } else if (this.user.username !== this.originalUsername && this.availableUsernames.includes(this.user.username)) {
                // Check uniqueness only if username has changed AND it exists in the list
                this.errors.username = 'This username is already taken.';
                isValid = false;
            }

            // Email validation
            if (!this.user.email) {
                this.errors.email = 'Email is required.';
                isValid = false;
            } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.user.email)) {
                this.errors.email = 'Invalid email format.';
                isValid = false;
            }

            return isValid;
        },

        /**
         * Handles the profile update submission.
         * Performs validation and sends data to the backend.
         */
        async updateProfile() {
            if (!this.validateForm()) {
                toast.error('Please correct the errors in the form.', { position: 'top-center' });
                return;
            }

            this.isLoading = true;
            try {
                const token = localStorage.getItem('access_token');
                const response = await fetch('http://127.0.0.1:5000/update_user_info', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`,
                    },
                    body: JSON.stringify({
                        name: this.user.name,
                        username: this.user.username,
                        email: this.user.email,
                    }),
                });

                if (response.ok) {
                    toast.success('Profile updated successfully!', { position: 'top-center' });
                    // Update originalUsername in case it was changed successfully
                    this.originalUsername = this.user.username;
                    // Re-fetch usernames to ensure the list is up-to-date for future validations
                    await this.fetchUsernames();
                } else {
                    const errorData = await response.json();
                    toast.error(errorData.message || 'Failed to update profile.', { position: 'top-center' });
                }
            } catch (error) {
                console.error('Error updating profile:', error);
                toast.error('Server error during profile update.', { position: 'top-center' });
            } finally {
                this.isLoading = false;
            }
        },
    },
};
</script>

<style scoped>
.container {
    max-width: 800px;
}

.card {
    border-radius: 10px;
}

.form-control:focus {
    box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
    border-color: #86b7fe;
}
</style>