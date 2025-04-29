<template>
  <div class="dashboard">
    <div class="spaces-container">
      <transition-group name="space-fade" tag="div" class="spaces-list">
        <div v-for="space in spaces" :key="space.id" class="space-card" @click="selectSpace(space)">
          <h3>{{ space.name }}</h3>
          <div class="factors">
            <span v-for="(factor, index) in space.factors" :key="index">
              {{ factor }}
            </span>
          </div>
        </div>
      </transition-group>
    </div>

    <button class="add-space-btn" @click="showSpaceForm = true">
      <span>+</span> Add Space
    </button>

    <div v-if="showSpaceForm" class="modal-overlay" @click.self="showSpaceForm = false">
      <div class="space-form">
        <h3>Create New Space</h3>
        <input v-model="newSpace.name" type="text" placeholder="Space name" class="form-input">
        <div class="factors-input">
          <div v-for="(factor, index) in newSpace.factors" :key="index" class="factor-item">
            <input v-model="newSpace.factors[index]" type="text" placeholder="Factor name" class="form-input">
            <button @click="removeFactor(index)" class="remove-factor">×</button>
          </div>
          <button @click="addFactor" class="add-factor">+ Add Factor</button>
        </div>
        <div class="form-actions">
          <button @click="createSpace" class="submit-btn">Create</button>
          <button @click="showSpaceForm = false" class="cancel-btn">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      spaces: [],
      showSpaceForm: false,
      newSpace: {
        name: '',
        factors: ['']
      },
      apiBaseUrl: 'http://localhost:5000/api' // Update if your Flask runs on different port
    }
  },
  created() {
    this.fetchSpaces()
  },
  methods: {
    async fetchSpaces() {
      try {
        const response = await axios.get(`${this.apiBaseUrl}/spaces`)
        this.spaces = response.data
      } catch (error) {
        console.error('Error fetching spaces:', error)
      }
    },
    addFactor() {
      this.newSpace.factors.push('')
    },
    removeFactor(index) {
      if (this.newSpace.factors.length > 1) {
        this.newSpace.factors.splice(index, 1)
      }
    },
    async createSpace() {
      if (this.newSpace.name.trim() === '') return

      // Remove empty factors
      const factors = this.newSpace.factors.filter(f => f.trim() !== '')

      try {
        const response = await axios.post(`${this.apiBaseUrl}/spaces`, {
          name: this.newSpace.name,
          factors: factors
        })

        // Add the new space to our local state
        this.spaces.push({
          id: response.data.id,
          name: response.data.name,
          factors: factors
        })

        // Reset form
        this.newSpace = {
          name: '',
          factors: ['']
        }
        this.showSpaceForm = false
      } catch (error) {
        console.error('Error creating space:', error)
      }
    },
    selectSpace(space) {
      this.$router.push(`/spaces/${space.id}`)
    }
  }
}
</script>

<style scoped>
.dashboard {
  display: flex;
  height: 100vh;
  position: relative;
}

.spaces-container {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f5f7fa;
}

.spaces-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.space-card {
  background: white;
  border-radius: 10px;
  padding: 20px;
  width: 250px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  border-left: 4px solid #4CAF50;
}

.space-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
}

.space-card h3 {
  margin-top: 0;
  color: #2c3e50;
}

.factors {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 15px;
}

.factors span {
  background: #e0f7fa;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #00838f;
}

.add-space-btn {
  position: fixed;
  right: 30px;
  top: 30px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 50px;
  padding: 15px 25px;
  font-size: 16px;
  cursor: pointer;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.add-space-btn:hover {
  background: #388E3C;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
}

.add-space-btn span {
  font-size: 20px;
  font-weight: bold;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.space-form {
  background: white;
  padding: 30px;
  border-radius: 10px;
  width: 400px;
  max-width: 90%;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.space-form h3 {
  margin-top: 0;
  color: #2c3e50;
}

.form-input {
  width: 100%;
  padding: 10px;
  margin-bottom: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.factors-input {
  margin-bottom: 20px;
}

.factor-item {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}

.factor-item input {
  flex: 1;
}

.remove-factor {
  background: #ff5252;
  color: white;
  border: none;
  border-radius: 50%;
  width: 25px;
  height: 25px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-factor {
  background: none;
  border: 1px dashed #4CAF50;
  color: #4CAF50;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.add-factor:hover {
  background: #e8f5e9;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.submit-btn {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}

.cancel-btn {
  background: #f5f5f5;
  color: #666;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
}

/* Animation */
.space-fade-enter-active,
.space-fade-leave-active {
  transition: all 0.5s ease;
}

.space-fade-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.space-fade-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}
</style>