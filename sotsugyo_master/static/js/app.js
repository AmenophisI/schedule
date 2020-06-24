const hum = document.querySelector('.hum_menu');
const link = document.querySelector('.hum_link');

hum.addEventListener('click',()=>{
    link.classList.toggle('open')
})