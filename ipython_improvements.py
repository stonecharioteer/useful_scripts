def code_toggler(debug=None):
    from IPython.display import HTML
    if debug is not None:
        debug = True
    else:
        debug = False
    script = """<script>
    code_show=%s; 
    function code_toggle() {
     if (code_show){
     $('div.input').hide();
     } else {
     $('div.input').show();
     }
     code_show = !code_show
    } 
    $( document ).ready(code_toggle);

    code_show_err=%s; 
    function code_show_err_func() {
     if (code_show_err){
     $('div.output_stderr').hide();
     } else {
     $('div.output_stderr').show();
     }
     code_show_err = !code_show_err
    } 
    $( document ).ready(code_show_err_func);
    </script>\n"""%("false" if debug else "true", "false" if debug else "true")
    html = 'Click <a href="javascript:code_toggle()">here</a> to toggle code and <a href="javascript:code_show_err_func()">here</a> to toggle warnings.'
    return HTML(script+html)
