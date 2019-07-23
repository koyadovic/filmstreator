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
    }
});
