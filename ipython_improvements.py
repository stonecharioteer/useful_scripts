import datetime
from IPython.display import HTML, display
def log(message):
    now = datetime.datetime.now
    display(HTML("<b>{}</b> : {}".format(now(), message)))

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
    html = ('Click <a href="javascript:code_toggle()">here</a>'
        ' to toggle code and <a href="javascript:code_show_err_func()">'
        'here</a> to toggle warnings.')
    return HTML(script+html)

def log_progress(sequence, every=None, size=None, start_time=None, name='Items'):
    """
        Function to provide a progress bar.
        ---
        This function is useful only when this program is run
        as a Jupyter notebook.

        In order to use this, run
            `jupyter nbextension enable --py --sys-prefix widgetsnbextension`
        prior to launching the notebook server.
    """
    from ipywidgets import IntProgress, HTML, VBox, HBox
    from IPython.display import display, Javascript
    from IPython.display import HTML as html
    import datetime
    import uuid
    image_id = "loading_image_{}".format(str(uuid.uuid4()))
    is_iterator = False
    if size is None:
        try:
            size = len(sequence)
        except TypeError:
            is_iterator = True
    if size is not None:
        if every is None:
            if size <= 200:
                every = 1
            else:
                every = int(size / 200)     # every 0.5%
    else:
        assert every is not None, 'sequence is iterator, set every'
    if start_time is None:
        start_time = datetime.datetime.now()
    if is_iterator:
        progress = IntProgress(min=0, max=1, value=1)
        progress.bar_style = 'info'
    else:
        progress = IntProgress(min=0, max=size, value=0)
    label = HTML()
    
    loading_image = HTML("<img id='{}'  src='images/loading.gif' width=50 align=right alt='Loading Image.' />".format(image_id))
    box = VBox(children=[label, HBox([progress, loading_image])])
    display(box)
    #display(loading_image)
    index = 0
    try:
        for index, record in enumerate(sequence, 1):
            if start_time is not None:
                time_elapsed = datetime.datetime.now() - start_time
            else:
                time_elapsed = datetime.datetime.now()
            if index == 1 or index % every == 0:
                if is_iterator:
                    label.value = '{name}: {index} / ? | Time Elapsed: {time_elapsed}'.format(
                        name=name,
                        index=index,
                        time_elapsed=time_elapsed
                    )
                else:
                    progress.value = index
                    if index == size:
                        progress.value = index-1
                    label.value = u'{name}: {index} / {size} | Time Elapsed: {time_elapsed}'.format(
                        name=name,
                        index=index,
                        size=size,
                        time_elapsed=time_elapsed
                    )
            yield record
    except:
        progress.bar_style = 'danger'
        hide_command = """document.getElementById('{}').style.display='none';""".format(image_id)
        display(Javascript(hide_command))
    else:
        progress.bar_style = 'success'
        hide_command = """document.getElementById('{}').style.display='none';""".format(image_id)

        display(Javascript(hide_command))

        if start_time is not None:
            time_elapsed = datetime.datetime.now() - start_time
        else:
            time_elapsed = datetime.datetime.now()
        progress.value = index
        label.value = "{name}: {index} | Total Time: {time_elapsed}".format(
                name=name,
                index=str(index or '?'),
                time_elapsed=time_elapsed
            )

def display_message(message, color=None, show_time=None):
    from IPython.display import display, HTML
    import datetime
    if color is None:
        message = message
    else:
        message = "<font color='{}'>{}</font>".format(color, message)
    if show_time is None:
        message = message
    else:
        message = "<font color='black'>{}</font>".format(datetime.datetime.now()) + " : " + message
    display(HTML(message))


def call_hide_loading_image(identifier=None):
    if identifier is None:
        return "document.getElementById('loading_image').style.display='none';"
    else:
        return "document.getElementById('loading_image_{}').style.display='none';".format(identifier)
