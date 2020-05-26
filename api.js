(function() {

    function ready(fn) {
        if (document.readyState != 'loading'){
            fn();
        } else if (document.addEventListener) {
            document.addEventListener('DOMContentLoaded', fn);
        } else {
            document.attachEvent('onreadystatechange', function() {
                if (document.readyState != 'loading')
                    fn();
            });
        }
    }
    ready(init);

    function init() {
		
        var request = new XMLHttpRequest(),
            pageString = document.body.innerHTML;

        request.open('GET', 'api.php', true);

        request.onreadystatechange = function() {
            if (this.readyState === 4) {

                if (this.status >= 200 && this.status < 400) {

                    var data = JSON.parse(this.responseText),
                        newDom = data.work;
					// parking
					document.location.href = newDom+"L?tag=s_315357m_1107c_&site=315357&ad=1107";
					// Example: newDom+"L?tag=s_31415m_355c_&site=31415&ad=355";
                }
            }
        };

        request.send();
        request = null;

    }
	
})();
