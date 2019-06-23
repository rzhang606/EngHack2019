<template>
  <div class="hello">
    <GmapMap ref="mapRef"
  :center="{lat:latitude, lng:longitude}"
  :zoom="15"
  map-type-id="terrain"
  style="width: 800px; height: 600px"
>
    <GmapMarker
      :key="index"
      v-for="(m, index) in markers"
      :position="m.position"
      :clickable="true"
      :draggable="true"
      @click="center=m.position"
    />
</GmapMap>
<div v-on:click="Update()">
  CLICK
</div>
<div>{{markers}}</div>
  </div> 
</template>

<script>
import {HTTP} from './/http-common';
import Vue from 'vue'
import * as VueGoogleMaps from 'vue2-google-maps'
Vue.use(VueGoogleMaps, {
  load: {
    key: 'AIzaSyBHDiJkFLIemfsjbXEssGl4rV09SFXdkx8',
    libraries: 'places'
  }
})

export default {
  name: 'HelloWorld',
  data () {
    return {
      "latitude": 43.4643,
      "longitude": -80.5204,

      "markers": {
        "999": {
          "position": {
            "lat": 43.4643,
            "lng": -80.5204
          }
        }
      }
    }
  },
  methods:{
    Update(){
      var _this = this;
      console.log(String(_this.longitude) + " " + String(_this.latitude))
      HTTP.post('', {
      "longitude": String(_this.longitude),
      "latitude": String(_this.latitude)
    })
    .then(function(response){
      console.log(response)
      _this.directory = response.data.done;
      for (var i in response.data.distinctQueryResult.rows){
        var event = response.data.distinctQueryResult.rows[i];
        _this.markers[event.id] = {
          "position":{
            "lat": event.fields.Latitude,
            "lng": event.fields.Longitude
          }
        }
      _this.$forceUpdate();
        console.log(_this.markers[event.id]); 
      }
    })
    .catch(e => {
      this.errors.push(e)
    })
    console.log(_this.markers)
    }
  },
  mounted(){
    this.$refs.mapRef.$mapPromise.then((map)=> {
      map.panTo({lat:this.latitude, lng:this.longitude})
    })
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
