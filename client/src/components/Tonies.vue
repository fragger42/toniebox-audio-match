<template>
  <label for="tonieselect">
    <select id="tonieselect" class="form-control" @change="tonieSelected">
      <option selected disabled>Wähle deinen Tonie</option>
      <option v-for="tonie in tonies" :key="tonie.id" :value="tonie.id">
        {{ tonie.name }}
      </option>
    </select>
  </label>
</template>

<script>
export default {
  props: {
    tonies: {
      type: String,
      required: true,
      default: '',
    },
    audiobookID: {
      type: String,
      required: true,
      default: '',
    },
  },
  methods: {
    tonieSelected(event) {
      // eslint-disable-next-line
      alert('Starting upload. Your tonie will be ready in a few minutes! :)');
      this.$emit('onchange', event.target.value, this.audiobookID);
    },
  },
};
</script>
