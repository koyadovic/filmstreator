var SearchPanel = {
    props: ['postTitle'],
    template: '<h3>{{ postTitle }}</h3>'
};


var GenresCarousel = {

};




var data = {
    name: 'Miguel',
    searchResults: [],
    landingGenres: [],
};


var vm = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: data,

    created: function () {
        this.loadLandingData();
    },

    methods: {
        loadLandingData: function () {
            axios.get('/api/v1/landing/').then(response => {
                this.landingGenres = [];
                let data = response.data;
                for (let key in data) {
                    let films = data[key];
                    if (films.length > 0) {
                        this.landingGenres.push({name: key, films: films});
                    }
                }
            });
        },
    },

    components: {
        'search-panel': SearchPanel,
        'genres-carousel': GenresCarousel
    }
});
