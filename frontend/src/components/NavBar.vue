<template>
    <nav class="navbar bg-dark text-light navbar-expand-lg" style="position: sticky; top: 0; z-index: 1030;">
        <div class="container-fluid">
            <router-link class="navbar-brand text-primary fw-bold" to="/">Parking<font class="text-secondary">Pal</font>
            </router-link>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
                aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <!-- If Logged In and User -->
                <ul v-if="loggedIn && user && !user.admin" class="navbar-nav me-auto px-2">
                    <li class="nav-item px-2">
                        <router-link class="btn btn-outline-success" to="/user_dashboard">Home</router-link>
                    </li>
                    <li class="nav-item px-2">
                        <router-link class="btn btn-outline-primary" to="/summary">Summary</router-link>
                    </li>
                </ul>
                <!-- If Logged In and Admin -->
                <ul v-if="loggedIn && user && user.admin" class="navbar-nav ms-auto px-2">
                    <li class="nav-item px-2">
                        <router-link class="btn btn-outline-primary" to="/admin_dashboard">Home</router-link>
                    </li>
                    <li class="nav-item px-2">
                        <router-link class="btn btn-outline-primary" to="/user_management">Users</router-link>
                    </li>
                    <li class="nav-item px-2">
                        <router-link class="btn btn-outline-primary" to="/search">Search</router-link>
                    </li>
                    <li class="nav-item px-2">
                        <router-link class="btn btn-outline-primary" to="/admin_summary">Summary</router-link>
                    </li>
                </ul>

                <ul v-if="loggedIn" class="navbar-nav ms-auto px-2">
                    <li v-if="user" class="nav-item px-2">
                        <router-link class="nav-link">
                            {{ user.username }}
                        </router-link>
                    </li>
                    <li class="nav-item px-2">
                        <button class="btn btn-danger" @click="logout">Logout</button>
                    </li>
                </ul>
                <ul v-else class="navbar-nav ms-auto px-2">
                    <li class="nav-item px-2">
                        <router-link class="nav-link" to="/register">Register</router-link>
                    </li>
                    <li class="nav-item px-2">
                        <router-link class="nav-link" to="/login">Login</router-link>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
</template>

<style scoped>
.nav-link {
    color: #eeeeee
}

.nav-link:hover {
    color: #eeeeee
}

.router-link-active.nav-link,
.router-link-exact-active.nav-link {
    color: var(--bs-success);
    font-weight: 500;
}
</style>

<script>
import userMixin from '@/mixins/userMixin';
export default {
    name: 'NavBar',
    mixins: [userMixin],
};
</script>