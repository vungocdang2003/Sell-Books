function addReview(sanpham_id, khachhang_id){
    if (khachhang_id == ''){
        pathname = window.location.pathname
        let msg = "Ban can dang nhap de viet binh luan!!"
        window.location.href = "/dangnhap?msg = "+msg+"&next = "+pathname
    }
    else{
        let binhluan = document.getElementById('binhluan')
        fetch("api/binhluan",{
            method: "post",
            body: JSON.stringify({
                "sanpham_id": sanpham_id,
                "khachhang_id": khachhang_id,
                "binhluan": binhluan.value
            }),
            headers: {
                'Content-Type': 'aplication/json'
            }
        }).then(function(res){
            return res.json();
        }).then(function(data){
            if (data == false)
                alert("Ban can mua san pham de viet binh luan!!")
            else
                window.location.href = window.location.pathname;
        });
    }
}