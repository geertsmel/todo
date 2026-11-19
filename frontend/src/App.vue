<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import TodoList from './components/TodoList.vue'
import StatsPage from './components/StatsPage.vue'

// Navigation simple, sans bibliothèque : la page affichée dépend de la partie après # dans l'adresse
const currentPage = () => (window.location.hash === '#/stats' ? 'stats' : 'list')
const page = ref(currentPage())
const update = () => {
  page.value = currentPage()
}

onMounted(() => window.addEventListener('hashchange', update))
onBeforeUnmount(() => window.removeEventListener('hashchange', update))
</script>

<template>
  <nav class="tabs" aria-label="Pages">
    <a href="#/" :class="{ active: page === 'list' }" :aria-current="page === 'list' ? 'page' : undefined">Liste</a>
    <a href="#/stats" :class="{ active: page === 'stats' }" :aria-current="page === 'stats' ? 'page' : undefined">
      Statistiques
    </a>
  </nav>

  <TodoList v-if="page === 'list'" />
  <StatsPage v-else />
</template>
