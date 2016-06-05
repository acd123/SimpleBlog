KindEditor.ready(function(K) {
                K.create('textarea[name=content]',{
                    width:'600px',
                    height:'200px',
                    uploadJson: '/admin/upload/kindeditor', //django-url里匹配的路径
                });
        });