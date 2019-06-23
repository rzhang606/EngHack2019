<template>
  <div>
    <img src="../assets/logo.png" class="app">
  <div class="checks">
  <input class = "checkbox" v-model="included.food" type="checkbox">Food</input>
  <input class = "checkbox" v-model="included.shopping" type="checkbox">Shopping</input>
  <input class = "checkbox" v-model="included.washrooms" type="checkbox">Washrooms</input>
  <input class = "checkbox" v-model="included.garbage" type="checkbox">Garbage Cans</input>
  <input class = "checkbox" v-model="included.events" type="checkbox">Events</input><br><br>

  </div><br>
  <div class="app checks">Add Event: </div>
  <input type="text" class="app checks" v-model="eventname"></input>
  <div class="app checks">  Type: </div>
  <select v-model="eventtype" class="app checks">
    <option value="food">Food</option>
    <option value="shopping">Shopping</option>
    <option value="washrooms">Washrooms</option>
    <option value="garbage">Garbage Can</option>
    <option value="events">Event</option>
  </select><br><br>
  <div class="app checks">  Description: </div>
  <input type="text" class="app checks w500" v-model="eventdescription"></input><br><br>
  <div v-on:click="createEvent()" class="w500 button"> Create </div><br><br>
    <GmapMap ref="mapRef" class="map"
  :center="{lat:latitude, lng:longitude}"
  :zoom="20"
  map-type-id="terrain"
  style="width: 100%; height: 700px"
>
<gmap-info-window :options="infoOptions" :position="infoWindowPos" :opened="infoWinOpen" @closeclick="infoWinOpen=false">
            <div>{{infoTitle}}</div>
            <div>{{infoContent}}</div>
      </gmap-info-window>
    
        <GmapMarker
      :key="index"
      v-for="(m, index) in computed_food_markers"
      :position="m.position"
      :clickable="true"
      :draggable="false"
      :icon="{url: require('../assets/food.png')}"
      @click="center=toggleInfoWindow(m, index)"
    />
    <GmapMarker
      :key="index"
      v-for="(m, index) in computed_shopping_markers"
      :position="m.position"
      :clickable="true"
      :draggable="false"
      :icon="{url: require('../assets/shopping.png')}"
      @click="center=toggleInfoWindow(m, index)"
    />
    <GmapMarker
      :key="index"
      v-for="(m, index) in computed_garbage_markers"
      :position="m.position"
      :clickable="true"
      :draggable="false"
      :icon="{url: require('../assets/garbage.png')}"
      @click="center=toggleInfoWindow(m, index)"
    />
    <GmapMarker
      :key="index"
      v-for="(m, index) in computed_washrooms_markers"
      :position="m.position"
      :clickable="true"
      :draggable="false"
      :icon="{url: require('../assets/washrooms.png')}"
      @click="center=toggleInfoWindow(m, index)"
    />
    <GmapMarker
      :key="index"
      v-for="(m, index) in computed_events_markers"
      :position="m.position"
      :clickable="true"
      :draggable="false"
      :icon="{url: require('../assets/events.png')}"
      @click="center=toggleInfoWindow(m, index)"
    />
    
</GmapMap>
<!-- <div>{{computed_markers}}</div> -->
<!-- <div>{{food_markers}}</div>
<div>{{shopping_markers}}</div>
<div>{{washrooms_markers}}</div>
<div>{{garbage_markers}}</div> -->
  </div> 
</template>

<script>
import VueGeolocation from 'vue-browser-geolocation';
import {HTTP} from './/http-common';
import {HTTP2} from './/http-common';
import Vue from 'vue'
import * as VueGoogleMaps from 'vue2-google-maps'
Vue.use(VueGoogleMaps, {
  load: {
    key: 'AIzaSyBHDiJkFLIemfsjbXEssGl4rV09SFXdkx8',
    libraries: 'places'
  }
})
Vue.use(VueGeolocation);

export default {
  name: 'HelloWorld',
  data () {
    return {
      "eventname": "",
      "eventtype": "",
      "eventdescription": "",
      "included":{
        "food": true,
        "shopping": true,
        "washrooms": true,
        "garbage": true,
        "events": true
      },
      "infoTitle": '',
      "infoContent": '',
      "infoWindowPos": null,
      "infoWinOpen": false,
      "currentMidx": null,
      //optional: offset infowindow so it visually sits nicely on top of our marker
      "infoOptions": {
          "pixelOffset": {
          "width": 0,
          "height": -35
          }
      },
      "latitude": 43.4643,
      "longitude": -80.5204,

      "food_markers": {},
      "shopping_markers": {},
      "washrooms_markers": {},
      "garbage_markers": {},
      "events_markers": {}
    }
  },
  computed:{
    computed_food_markers: function(){
      if(!this.included.food)
        return {};
      return this.food_markers;
    },
    computed_shopping_markers: function(){
      if(!this.included.shopping)
        return {};
      return this.shopping_markers;
    },
    computed_garbage_markers: function(){
      if(!this.included.garbage)
        return {};
      return this.garbage_markers;
    },
    computed_washrooms_markers: function(){
      if(!this.included.washrooms)
        return {};
      return this.washrooms_markers;
    },
    computed_events_markers: function(){
      if(!this.included.washrooms)
        return {};
      return this.events_markers;
    }
  },
  methods:{
    maintain(){
      setInterval(this.Update(), 10);
    },
    Update(){
      var _this = this;
      // console.log(String(_this.longitude) + " " + String(_this.latitude))
      HTTP.post('', {
      "longitude": String(_this.longitude),
      "latitude": String(_this.latitude)
    })
    .then(function(response){
      // console.log(response)
      // _this.directory = response.data.done;
      for (var i in response.data.distinctQueryResult.rows){
        var event = response.data.distinctQueryResult.rows[i];
        // _this.markers[event.fields.Type][event.id] 
        var input = {
          "position":{
            "lat": event.fields.Latitude,
            "lng": event.fields.Longitude
          },
          "description": event.fields.Description,
          "title": event.fields.Event,
          "type": event.fields.Type,
          "id": event.id
        }
        if(event.fields.Type == "food")
          _this.food_markers[event.id] = input;
        else if(event.fields.Type == "shopping")
          _this.shopping_markers[event.id] = input;
        else if(event.fields.Type == "washrooms")
          _this.washrooms_markers[event.id] = input;
        else if(event.fields.Type == "garbage")
          _this.garbage_markers[event.id] = input;
        else if(event.fields.Type == "events")
          _this.events_markers[event.id] = input;
      _this.$forceUpdate();
        // console.log(_this.markers[event.id]); 
      }
    })
    .catch(e => {
      this.errors.push(e)
    })
    // console.log(_this.markers)
    },
    toggleInfoWindow: function(marker, idx) {
            this.infoWindowPos = marker.position;
            this.infoContent = marker.description;
            this.infoTitle = marker.title;

            //check if its the same marker that was selected if yes toggle
            if (this.currentMidx == idx) {
              this.infoWinOpen = !this.infoWinOpen;
            }
            //if different marker set infowindow to open and reset current marker index
            else {
              this.infoWinOpen = true;
              this.currentMidx = idx;

            }
    },
    createEvent(){
      var _this = this;
      // console.log(String(_this.longitude) + " " + String(_this.latitude))
      HTTP2.post('', {
      "event": _this.eventname,
      "type": _this.eventtype,
      "description": _this.eventdescription,
      "longitude": String(_this.longitude),
      "latitude": String(_this.latitude)
    })
    .then(function(response){
      console.log(response)
      // _this.directory = response.data.done;
      // for (var i in response.data.distinctQueryResult.rows){
      //   var event = response.data.distinctQueryResult.rows[i];
      //   // _this.markers[event.fields.Type][event.id] 
      //   var input = {
      //     "position":{
      //       "lat": event.fields.Latitude,
      //       "lng": event.fields.Longitude
      //     },
      //     "description": event.fields.Description,
      //     "title": event.fields.Event,
      //     "type": event.fields.Type,
      //     "id": event.id
      //   }
      //   if(event.fields.Type == "food")
      //     _this.food_markers[event.id] = input;
      //   else if(event.fields.Type == "shopping")
      //     _this.shopping_markers[event.id] = input;
      //   else if(event.fields.Type == "washrooms")
      //     _this.washrooms_markers[event.id] = input;
      //   else if(event.fields.Type == "garbage")
      //     _this.garbage_markers[event.id] = input;
      //   else if(event.fields.Type == "events")
      //     _this.events_markers[event.id] = input;
      // _this.$forceUpdate();
        // console.log(_this.markers[event.id]); 
      // }
    })
    .catch(e => {
      this.errors.push(e)
    })
    // console.log(_this.markers)
    }
  },
  mounted(){
    this.$getLocation().then(coordinates => {
      console.log(coordinates);
      this.latitude = coordinates.lat;
      this.longitude = coordinates.lng;
    });
    this.$refs.mapRef.$mapPromise.then((map)=> {
      map.panTo({lat:this.latitude, lng:this.longitude})
    });
    this.maintain();
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
.app {
  text-align: left;
  display: inline-flex;
}
.map {
  margin:auto
}
.checkbox {
  display: inline-block;
  padding: 5px;
  font-size: xx-large;
  width: 40px;
  height: 40px;
  /* font-size-adjust: inherit; */
  margin:right;
  fill: #42b983;
}
.w500{
  width:100%
}
.button{
  align-content: center;
  text-align: center;
  height: 50px;
  font-size: 30px;
  border-radius: 10px;
  background-color: rgb(34, 177, 76);
  color: white;
  font-family: Verdana, Geneva, sans-serif;
  cursor: pointer;
  font-style:
}
.checks{
  display: inline-block;
  font-size: 40px;
  padding-left: 25px;
  /* width: 50px; */
  fill:#42b983;
}
</style>
