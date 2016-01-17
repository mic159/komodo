import json

from python_dashing.option_spec.import_line import import_line_spec

from input_algorithms.spec_base import boolean, string_spec, listof, overridden, or_spec, integer_spec
from input_algorithms.dictobj import dictobj

from textwrap import dedent

class SourceSpec(dictobj.Spec):
    url = dictobj.Field(
          string_spec
        , help = "URL to load the source data from"
        )

    interval = dictobj.Field(
          integer_spec
        , help = "How long in milliseconds to poll"
        )

class Dashboard(dictobj.Spec):
    description = dictobj.Field(
          string_spec
        , default = "{_key_name_1} Dashboard"
        , formatted = True
        , help = "Description to show up in the index"
        )

    path = dictobj.Field(
          overridden("{_key_name_1}")
        , formatted = True
        , help = "Url path to the dashboard"
        )

    es6 = dictobj.Field(
          string_spec
        , help = "Extra es6 javascript to add to the dashboard module"
        )

    sources = dictobj.Field(
          SourceSpec.FieldSpec()
        , wrapper=listof
        , help = "Definition of source objects"
        )

    is_index = dictobj.Field(
          boolean
        , formatted = True
        , help = "Whether this page is an index or not"
        )

    layout = dictobj.Field(
          string_spec
        , help = "Reactjs xml for the laytout of the dashboard"
        )

    imports = dictobj.Field(
          lambda: or_spec(string_spec(), listof(import_line_spec()))
        , help = "es6 imports for the dashboard"
        )

    enabled_modules = dictobj.Field(
          string_spec
        , formatted = True
        , wrapper = listof
        , help = "The modules to enable for this dashboard"
        )

    def make_dashboard_module(self, modules):
        imports = []
        for imprt in self.imports:
            if hasattr(imprt, "import_line"):
                imports.append(imprt.import_line(modules))
            else:
                imports.append(imprt)

        sources = json.dumps({"sources": [x.as_dict() for x in self.sources]})

        return dedent("""
            import styles from "/modules/python_dashing.server/Dashboard.css";
            import React, {{Component}} from 'react';
            import ReactDOM from 'react-dom';
            {imports}

            class Dashboard extends Component {{
                constructor(props) {{
                    super(props);
                    this.state = {{data: {{}}}};
                }}
                refresh(url) {{
                    fetch(url)
                      .then(data => data.json())
                      .then(data => {{
                        let state = {{}};
                        state[url] = data;
                        this.setState(state);
                      }})
                }}

                componentDidMount() {{
                    this.props.sources.map((source) => {{
                        setInterval(this.refresh.bind(this), source.interval, source.url);
                    }});
                }}

                render() {{
                    return (
                        <div className={{styles.dashboard}}>
                            {layout}
                        </div>
                    )
                }};

                {es6}
            }}

            document.addEventListener("DOMContentLoaded", function(event) {{
                var element = React.createElement(Dashboard, {sources});
                ReactDOM.render(element, document.getElementById('page-content'));
            }});
        """).format(imports="\n".join(imports), layout=self.layout, es6=self.es6, sources=sources)

