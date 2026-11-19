<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../api.js'
import { STATUSES } from '../statuses.js'

const todos = ref([])
const newTitle = ref('')
const filter = ref('all')
const error = ref('')
const loading = ref(true)

async function run(action) {
  error.value = ''
  try {
    await action()
  } catch (e) {
    error.value = e.message
  }
}

const load = () =>
  run(async () => {
    todos.value = await api('/todos')
  })

const addTodo = () =>
  run(async () => {
    const title = newTitle.value.trim()
    if (!title) return
    const created = await api('/todos', { method: 'POST', body: JSON.stringify({ title }) })
    todos.value.push(created)
    newTitle.value = ''
  })

async function setStatus(todo, status) {
  await run(async () => {
    const updated = await api(`/todos/${todo.id}`, { method: 'PATCH', body: JSON.stringify({ status }) })
    Object.assign(todo, updated)
  })
  // En cas d'erreur, on recharge la liste pour que la liste déroulante affiche le vrai statut
  if (error.value) {
    try {
      todos.value = await api('/todos')
    } catch {
      /* l'erreur déjà affichée suffit */
    }
  }
}

const remove = (todo) =>
  run(async () => {
    await api(`/todos/${todo.id}`, { method: 'DELETE' })
    todos.value = todos.value.filter((t) => t.id !== todo.id)
  })

const visibleTodos = computed(() =>
  filter.value === 'all' ? todos.value : todos.value.filter((t) => t.status === filter.value),
)
const countOf = (key) => todos.value.filter((t) => t.status === key).length

onMounted(async () => {
  await load()
  loading.value = false
})
</script>

<template>
  <main class="card">
    <header>
      <h1>Ma liste de todos</h1>
      <p class="count">
        {{ countOf('todo') }} à faire · {{ countOf('in_progress') }} en cours · {{ countOf('done') }} terminée(s)
      </p>
    </header>

    <form class="add" @submit.prevent="addTodo">
      <input v-model="newTitle" type="text" maxlength="200" placeholder="Nouvelle tâche…" aria-label="Nouvelle tâche" />
      <button type="submit">Ajouter</button>
    </form>

    <p v-if="error" class="error" role="alert">{{ error }}</p>

    <nav class="filters" aria-label="Filtrer les tâches">
      <button :class="{ active: filter === 'all' }" @click="filter = 'all'">Toutes</button>
      <button v-for="s in STATUSES" :key="s.key" :class="{ active: filter === s.key }" @click="filter = s.key">
        {{ s.label }}
      </button>
    </nav>

    <p v-if="loading" class="empty">Chargement…</p>
    <p v-else-if="visibleTodos.length === 0" class="empty">Aucune tâche ici.</p>

    <ul v-else class="list">
      <li v-for="todo in visibleTodos" :key="todo.id" :class="{ done: todo.status === 'done' }">
        <span class="title">{{ todo.title }}</span>
        <select
          :value="todo.status"
          :class="['status', `status-${todo.status}`]"
          :aria-label="`Statut de ${todo.title}`"
          @change="setStatus(todo, $event.target.value)"
        >
          <option v-for="s in STATUSES" :key="s.key" :value="s.key">{{ s.single }}</option>
        </select>
        <button class="delete" @click="remove(todo)" :aria-label="`Supprimer ${todo.title}`">Supprimer</button>
      </li>
    </ul>
  </main>
</template>
