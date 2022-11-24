
let script = document.createElement("SCRIPT")
script.src = "https://cdn.jsdelivr.net/npm/axios@1.1.2/dist/axios.min.js"
document.head.appendChild(script)
function initJQuery(e) {
    var t;
    "undefined" == typeof jQuery ? ((t = document.createElement("SCRIPT")).src = "https://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js", t.type = "text/javascript", t.onload = e, document.head.appendChild(t)) : e()
}

initJQuery(function () {


        if (window.ShopifyAnalytics.meta.page.pageType === "product") {

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
                        console.log(response)
                            let box = document.getElementsByClassName('price__container')
                        response.forEach(combo=>{
                          let data = ''
                          let sum=0
                          let discount = combo.discount_amount
                          let discount_container = document.createElement("DIV")
                          const price_list =[]
                               combo.products.forEach(product=>{
                              let image_frame = document.createElement("IMG")
                              image_frame.src= product.image_url
                              data += product.product_name+" x"+product.quantity+"+"
                               discount_container.appendChild(image_frame)
                               let span = document.createElement("SPAN")
                               span.innerHTML= data
                               discount_container.appendChild(span)
                              price_list.push(product.product_price)
                            })
                             price_list.forEach(item=>{
                               sum += parseInt(item)
                             })


                          if(discount.charAt(discount.length-1)==='%'){
                              let percent =parseInt(combo.discount_amount.substring(0,combo.discount_amount.length))
                             let math = sum - sum * (percent /100)
                             let sub_string=data.substring(0,data.length-1)
                             sub_string += "=" +math.toString()
                            let children = document.createElement("DIV")
                            children.innerHTML = sub_string
                            box[0].appendChild(children)
                           }
                          else{
                              let amount =parseInt(combo.discount_amount)
                             let math = sum - amount
                             let sub_string=data.substring(0,data.length-1)
                             sub_string += "=" +math.toString()
                            let children = document.createElement("DIV")
                            children.innerHTML = sub_string
                            box[0].appendChild(children)
                          }


                        })

                    }
                })

            }


        // let children = document.createElement("DIV")
        // children.innerHTML = "HELLO"
        // box[0].appendChild(children)


        }
    }
)




