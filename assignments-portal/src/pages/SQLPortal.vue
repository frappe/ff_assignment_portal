<template>
    <div>
        <h1>SQL Portal</h1>

        <p>Problem Set name: {{ route.params.psetName }}</p>
    </div>
</template>

<script setup>
import { useRoute } from 'vue-router';

const route = useRoute();
</script>
