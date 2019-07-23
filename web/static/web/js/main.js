var SearchPanel = {
    props: ['postTitle'],
    template: '<h3>{{ postTitle }}</h3>'
};


var GenresCarousel = {

};




var data = {
    name: 'Miguel'
};


var vm = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: data,

    created: function () {
        // `this` points to the vm instance
        console.log('Loaded');
    },
    components: {
        'search-panel': SearchPanel,
        'genres-carousel': GenresCarousel
    }
});
