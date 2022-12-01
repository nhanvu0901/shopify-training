
let script = document.createElement("SCRIPT")
script.src = "https://cdn.jsdelivr.net/npm/axios@1.1.2/dist/axios.min.js"
document.head.appendChild(script)
function initJQuery(e) {
    var t;
    "undefined" == typeof jQuery ? ((t = document.createElement("SCRIPT")).src = "https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js", t.type = "text/javascript", t.onload = e, document.head.appendChild(t)) : e()
}

initJQuery(function () {


        if (window.ShopifyAnalytics.meta.page.pageType === "product") {
            //bai 8 cau i
           function exchange_data(){
               var xmlhttp = new XMLHttpRequest();
                xmlhttp.timeout = 300;
               xmlhttp.open("GET", "https://shoplify-odoo.myshopify.com/cart.json");
               xmlhttp.setRequestHeader("Content-Type", "application/json");
                xmlhttp.onreadystatechange = function () {

                   if (xmlhttp.readyState === 4) {
                       if (xmlhttp.status === 200) {
                           console.log(xmlhttp.responseText);
                            var xhr = new XMLHttpRequest();
                           xhr.open("POST", "https://odoo.website/shopify/addtocart");
                           // xhr.timeout=2000
                           xhr.setRequestHeader("Content-Type", "application/json");
                           xhr.onreadystatechange = function () {
                               if (xhr.readyState === 4) {
                                   if (xhr.status === 200) {
                                       console.log(xhr.responseText);
                                   }
                               }
                           };
                           xhr.send(xmlhttp.responseText)
                       }
                   }
               };
               xmlhttp.send()

           }

            $( ".product-form__submit" ).on( "click",  function(){
                setTimeout(exchange_data,5000)

             });


            var currency='';


                    jQuery.ajax({
                        type: "GET",
                        url: window.shopUrl+"/admin/shop.json",

                        contentType: "application/json",
                        async:true,
                        crossDomain:true,
                        processData: false,
                        error: function (request, error) {
                            console.log(error)
                        },
                        complete(data_get) {
             //               currency =JSON.parse(data_get.responseText).shop.money_format.slice(-1)
             // console.log(currency)
            let url, id ,response= ''
            if (window.ShopifyAnalytics.meta.product) {
                id = window.ShopifyAnalytics.meta.product.id
                url = window.location.href
                param={
                    product_id:id,
                    product_handle:url
                }
                jQuery.ajax({
                        type: "POST",
                        url: "https://odoo.website/getdata",
                        data: JSON.stringify(param),
                        contentType: "application/json",
                        async:true,
                        crossDomain:true,
                        processData: false,
                        error: function (request, error) {
                            console.log(error)
                        },
                        complete(data) {
                        response = JSON.parse(JSON.parse(data.responseText).result)
                            let box = document.getElementsByClassName('price__container')
                            let add_to_cart_color =''

                        response.forEach(combo=>{
                            let color_font = combo.custom.font_color;
                            add_to_cart_color = combo.custom.add_to_cart_color;





                          let data = ''
                          let sum=0
                          let discount = combo.discount_amount
                          let discount_container = document.createElement("DIV")
                           discount_container.classList.add('discount-container')
                           let disccount_span = document.createElement("SPAN")
                            disccount_span.classList.add('discount-percent')
                           disccount_span.innerHTML = combo.discount_amount
                            discount_container.appendChild(disccount_span)
                          const price_list =[]
                               combo.products.forEach((product, index, arr)=>{
                               let image_frame = document.createElement("IMG")
                               image_frame.src = product.image_url

                              if(index !== arr.length - 1){
                                data = product.product_name+" x"+product.quantity+"+ "

                              }
                              else{
                                data = product.product_name+" x"+product.quantity
                              }


                              discount_container.appendChild(image_frame)
                              let span = document.createElement("SPAN")
                              span.classList.add('name-item')
                              span.innerHTML = data
                              span.style.color = color_font
                              discount_container.appendChild(span)


                              price_list.push(product.product_price)
                            })
                             let equal = document.createElement("SPAN")
                               equal.innerHTML = "="
                            discount_container.appendChild(equal)
                             price_list.forEach(item=>{
                               sum += parseInt(item)
                             })


                          if(discount.charAt(discount.length-1)==='%'){
                              let percent =parseInt(combo.discount_amount.substring(0,combo.discount_amount.length))
                             let math = sum - sum * (percent /100)

                             // data += "=" +math.toString()
                             let span = document.createElement("SPAN")
                              span.classList.add('price')
                             span.innerHTML =  math.toString()
                              discount_container.appendChild(span)


                            box[0].appendChild(discount_container)
                           }
                          else{
                              let amount =parseInt(combo.discount_amount)
                             let math = sum - amount

                             // data += "=" +math.toString()
                             let span = document.createElement("SPAN")

                              span.innerHTML =  math.toString()
                              span.classList.add('price')
                              discount_container.appendChild(span)



                            box[0].appendChild(discount_container)
                          }


                          document.head.innerHTML += `
                                          <style>
                                         @media screen and (min-width: 990px){
                                              .product__info-wrapper {
                                                padding: 0 0 0 0;
                                              }}
                                            .discount-container{
                                             display: flex;
                                             flex-direction: row;
                                             justify-content: flex-start;
                                             align-items: center;
                                            }
                                            .discount-container img {
                                              height: 10vh;
                                            }
                                            .discount-container .discount-percent{
                                                font-size: 2rem;
                                                color: red;
                                            }
                                            .discount-container .price{
                                                font-size: 2rem;
                                                color: red;
                                            }
                                           
                                          </style>`
                        })
                            $( ".product-form__submit" ).css( "background-color", add_to_cart_color );

                    }
                })

            }
                        }})


        }

    }
)




