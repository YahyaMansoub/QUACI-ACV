<template>
    <div class="space-details">
        <div class="header">
            <h2>{{ space.name }}</h2>
            <button @click="goBack" class="back-btn">← Back to Spaces</button>
        </div>

        <div class="houses-container">
            <div class="upload-section">
                <input type="file" ref="fileInput" @change="handleFileUpload" accept=".csv" style="display: none">
                <button @click="triggerFileInput" class="upload-btn">
                    Upload House CSV
                </button>
                <span v-if="uploading" class="upload-status">Uploading...</span>
            </div>

            <div class="houses-list">
                <div v-for="house in houses" :key="house.id" class="house-card">
                    <h3>{{ house.name }}</h3>
                    <div class="house-meta">
                        <span>Simulations: {{ house.simulations_count }}</span>
                        <span>Factors: {{ house.factors_count }}</span>
                    </div>
                    <button @click="analyzeHouse(house)" class="analyze-btn">Analyze</button>
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
            space: {},
            houses: [],
            uploading: false,
            apiBaseUrl: 'http://localhost:5000/api'
        }
    },
    created() {
        this.fetchSpaceDetails()
    },
    methods: {
        async fetchSpaceDetails() {
            try {
                const spaceId = this.$route.params.spaceId
                const response = await axios.get(`${this.apiBaseUrl}/spaces/${spaceId}`)
                this.space = response.data
                this.houses = response.data.houses || []
            } catch (error) {
                console.error('Error fetching space details:', error)
            }
        },
        triggerFileInput() {
            this.$refs.fileInput.click()
        },
        async handleFileUpload(event) {
            const file = event.target.files[0]
            if (!file) return

            this.uploading = true

            try {
                const formData = new FormData()
                formData.append('file', file)

                const response = await axios.post(
                    `${this.apiBaseUrl}/spaces/${this.$route.params.spaceId}/houses`,
                    formData,
                    {
                        headers: {
                            'Content-Type': 'multipart/form-data'
                        }
                    }
                )

                this.houses.push(response.data)
            } catch (error) {
                console.error('Error uploading house:', error)
                alert(`Error uploading file: ${error.response?.data?.error || 'Unknown error'}`)
            } finally {
                this.uploading = false
                event.target.value = '' // Reset file input
            }
        },
        analyzeHouse(house) {
            console.log('Analyzing house:', house)
            // You'll implement this later
        },
        goBack() {
            this.$router.push('/')
        }
    }
}
</script>

<style scoped>
.space-details {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.back-btn {
    background: #f5f5f5;
    border: none;
    padding: 10px 15px;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.2s;
}

.back-btn:hover {
    background: #e0e0e0;
}

.houses-container {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.upload-section {
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 15px;
}

.upload-btn {
    background: #4CAF50;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.2s;
}

.upload-btn:hover {
    background: #388E3C;
}

.upload-status {
    color: #666;
}

.houses-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
}

.house-card {
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    padding: 15px;
    transition: transform 0.2s, box-shadow 0.2s;
}

.house-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.house-meta {
    display: flex;
    justify-content: space-between;
    margin: 10px 0;
    color: #666;
    font-size: 14px;
}

.analyze-btn {
    background: #2196F3;
    color: white;
    border: none;
    padding: 8px 15px;
    border-radius: 4px;
    cursor: pointer;
    width: 100%;
    transition: background 0.2s;
}

.analyze-btn:hover {
    background: #1976D2;
}
</style>