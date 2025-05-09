<template>
  <div class="house-card">
    <div class="card-header">
      <h3>{{ house.name }}</h3>
    </div>
    <div class="card-body">
      <p><strong>Simulations:</strong> {{ house.simulations_count }}</p>
      <p><strong>Facteurs:</strong> {{ house.factors_count }}</p>
    </div>
    <div class="card-footer">
      <button class="action-btn">View Details</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HouseCard',
  props: {
    house: {
      type: Object,
      required: true
    }
  }
}
</script>


<style scoped>
.house-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  border-radius: 12px;
  background-color: #ffffff;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 20px;
  transition: transform 0.2s, box-shadow 0.2s;
  width: 250px;
  margin: 15px;
}

.house-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
}

.card-header h3 {
  margin: 0;
  font-size: 1.5rem;
  color: #2c3e50;
}

.card-body {
  margin-top: 10px;
  font-size: 1rem;
  color: #34495e;
}

.card-body p {
  margin: 5px 0;
}

.card-footer {
  margin-top: 15px;
  text-align: right;
}

.action-btn {
  background-color: #3498db;
  color: #ffffff;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s;
}

.action-btn:hover {
  background-color: #2980b9;
}
</style>
