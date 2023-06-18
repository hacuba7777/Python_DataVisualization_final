import dash
from dash import dcc
from dash import html
from urllib.request import urlopen
import json
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_bootstrap_templates import load_figure_template
import pandas as pd
import plotly.graph_objects as go
import plotly_express as px
import geopandas as gpd
geo_data = pd.read_csv('python final project/dataset/全國失業率_2022.csv')
town_shp = gpd.read_file("python final project/dataset/geo_taiwan_short.json")
geo_result = town_shp.merge(geo_data, left_on=('COUNTYNAME'), right_on=('項目別_Iterm'))
geo_fig = px.choropleth(geo_result, geojson=geo_result.geometry, locations=geo_result.index, color="2022")
geo_fig.update_geos(fitbounds="locations", visible=False)


SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20%",
    "padding": "2% 1%",
    "background-color": "#a0a8b0",
}

sidebar_left = html.Div(
    [
        html.H2("Menu"),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/home", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

df = px.data.gapminder()
df2 = pd.read_csv('python final project/dataset/全國失業率.csv',encoding='utf-8')
fig1 = px.bar(df[df.country.isin(['Taiwan','Japan'])],x='year',y='gdpPercap',color='country',barmode='group',height=600)
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)
df_map = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
                   dtype={"fips": str})
fig2 = px.scatter_matrix(df[df.country.isin(['Taiwan','Japan'])],dimensions=["year", "gdpPercap",'pop'], color="country" ,height=600)
# fig3 = px.choropleth(df_map, geojson=counties, locations='fips', color='unemp',
#                            color_continuous_scale="Viridis", 
#                            range_color=(0, 12),
#                            scope="usa",
#                            labels={'unemp':'unemployment rate'}
#                           )
# fig3.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig4 = px.bar(df2,x='項目別_Iterm',y='2022',color='項目別_Iterm',barmode='stack',height=600)

#fig5 折線圖
df3 = df2.set_index('項目別_Iterm') 
df3 = df3.transpose()  # 交換行列
fig5 = px.line(df3, x=df3.index, y=df3.columns, title='折線圖')
fig5.update_xaxes(title_text='年份')
fig5.update_yaxes(title_text='失業率')



sidebar = html.Div(
    [
        html.H1("資料視覺化--全國失業率", style={'text-align': 'center'}),
        dbc.Nav(
            [
                dbc.NavLink("Page 1", href="/page1", active="exact"),
                dbc.NavLink("Page 2", href="/page2", active="exact"),
                dbc.NavLink("Page 3", href="/page3", active="exact"),
                dbc.NavLink("Page 4", href="/page4", active="exact"), 
                dbc.NavLink("Page 5", href="/page5", active="exact"), 
            ],
            vertical=False,
            pills=True,
        ),
    ],
    className="sidebar",
)

content = html.Div(id="page-content", className="content")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SKETCHY])
app.title = "python final"
app.layout = dmc.MantineProvider(
    id="app-theme",
    theme={"colorScheme": "white",},
    inherit=True,
    withGlobalStyles=True,
    withNormalizeCSS=True,
    children = [
        dmc.Header(
                    height=90,
                    withBorder=True,
                    style={"padding": "16px", "display": "flex", "justifyContent": "space-between"},
                    children=[
                        dmc.Text(
                            style={"fontSize": 10},
                        ),
                        dmc.Switch(
                                id="switch-theme",
                                size="lg",
                                radius="sm",
                                label="Dark Mode",
                                checked=True
                            ),
                        ],
                ),
        html.Div(
            style={'width':'30%','flex':'1'},
            children=[
                dbc.Row([dbc.Col(sidebar_left),])]),
        html.Div(  
            style={'width':'90%','flex':'1','padding-left':'30%'},
            children=[
            dcc.RangeSlider(
                id='year-slider',
                min=df['year'].min(),
                max=df['year'].max(),
                value=[df['year'].max(),df['year'].min()],
                step=None,
                marks={str(year): str(year) for year in df['year'].unique()}
            ),
            dcc.Location(id='url', refresh=False),
            sidebar,
            content,
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': column, 'value': column} for column in df2.columns[0:]],
                value=df2.columns[1]
            ),
            html.Div(id='output-graph'),
            ]),
])
@app.callback(
    dash.dependencies.Output("page-content", "children"),
    dash.dependencies.Output('app-theme', 'theme'),
    dash.dependencies.Output('output-graph', 'children'),
    [dash.dependencies.Input("url", "pathname")],
    [dash.dependencies.Input('app-theme', 'theme')],
    [dash.dependencies.Input("switch-theme", "checked")],
    [dash.dependencies.Input('year-dropdown', 'value')],
    [dash.dependencies.Input("year-slider", "value")],
    prevent_intial_call=True
)
def render_page_content(pathname, current_theme, checked, year, fig1_year):
    data = df2[['項目別_Iterm', year]]

    fig = go.Figure(data=[
        go.Bar(x=data['項目別_Iterm'], y=data[year])
    ])
    fig.update_layout(title=f'Year {year} Data')
    fig1 = px.bar(df[(df.country.isin(['Taiwan','Japan']))&(df.year>=min(fig1_year))&(df.year<=max(fig1_year))],x='year',y='gdpPercap',color='country',barmode='group',height=600)
    if not checked:
        current_theme.update({'colorScheme': 'dark'})
        fig1.update_layout(paper_bgcolor='#1a1919')
        fig2.update_layout(paper_bgcolor='#1a1919')
        fig4.update_layout(paper_bgcolor='#1a1919')
        fig5.update_layout(paper_bgcolor='#1a1919')
        fig.update_layout(paper_bgcolor='#1a1919')
        geo_fig.update_layout(paper_bgcolor='#1a1919')
    else:
        current_theme.update({'colorScheme': 'white'})
        fig1.update_layout(paper_bgcolor='white')
        fig2.update_layout(paper_bgcolor='white')
        fig4.update_layout(paper_bgcolor='white')
        fig5.update_layout(paper_bgcolor='white')
        fig.update_layout(paper_bgcolor='white')
        geo_fig.update_layout(paper_bgcolor='white')

    if pathname == "/page1":
        return dcc.Graph(id='fig1', figure=fig1), current_theme, dcc.Graph(figure=fig)
    elif pathname == "/page2":
        return dcc.Graph(id='fig2', figure=fig2), current_theme, dcc.Graph(figure=fig)
    elif pathname == "/page3":
        return dcc.Graph(id='fig4', figure=fig4), current_theme, dcc.Graph(figure=fig)
    elif pathname == "/page4":
        return dcc.Graph(id='fig5', figure=fig5), current_theme, dcc.Graph(figure=fig)
    elif pathname == "/page5":
        return dcc.Graph(id='geo_fig', figure=geo_fig), current_theme, dcc.Graph(figure=fig)
    else:
        return html.H1("Home"), current_theme, dcc.Graph(figure=fig)

if __name__ == "__main__":
    app.config.suppress_callback_exceptions = True
    app.run_server(debug=True)