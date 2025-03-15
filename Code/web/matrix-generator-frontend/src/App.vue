<template>
  <div>
    <h1>DataFrame Input</h1>
    <textarea v-model="dataframeInput" placeholder="Paste your DataFrame here"></textarea>
    
    <h1>Matrix Generator</h1>
    <div v-for="(column, index) in columns" :key="index">
      <label :for="'column-' + index">Column {{ index + 1 }}:</label>
      <select :id="'column-' + index" v-model="column.distribution">
        <option value="random">Random</option>
        <option value="normal">Normal Distribution</option>
        <option value="uniform">Uniform Distribution</option>
      </select>
    </div>
    <button @click="generateMatrix">Generate Matrix</button>
    
    <h2>Generated Matrix</h2>
    <pre>{{ generatedMatrix }}</pre>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      dataframeInput: '',
      columns: [],
      generatedMatrix: []
    };
  },
  methods: {
    parseDataframe() {
      try {
        const df = JSON.parse(this.dataframeInput);
        this.columns = Object.keys(df).map(key => ({
          name: key,
          distribution: 'random'
        }));
      } catch (e) {
        console.error('Invalid DataFrame input', e);
      }
    },
    async generateMatrix() {
      const payload = {
        columns: this.columns,
        dataframe: JSON.parse(this.dataframeInput)
      };

      try {
        const response = await axios.post('http://localhost:5000/generate-matrix', payload);
        this.generatedMatrix = response.data.matrix;
      } catch (error) {
        console.error('Error generating matrix:', error);
      }
    }
  },
  watch: {
    dataframeInput: 'parseDataframe'
  }
};
</script>

<style scoped>
textarea {
  width: 100%;
  height: 100px;
}
</style>