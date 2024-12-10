<#
multi line comment
#>
# single line comment


include lib
from folder.subfolder include file

_scree = {
  color: red,
  draw_hide:draw,
  shape: square,
  height: 128,
  width: 72,
  position_xy: [20,20],
  repeat_by: 4,4
}    



greet_user(){
  <#
    greet_user
  #>
}

change_color(_scree,_nilo){
  _scree.children.X1Y1: style
  _nilo.color: green
  _scree = {
    color: red,
    draw_hide: draw,
  }
}

containers = [_container1,_scree]  


for container in containers:
  container.color = red
  if container == _container1:
    container = {
      draw_hide: hide,
    }

main _screen = {                         
  color: green,              
  draw_hide: draw,         
  shape: circle,
  height: 1280,
  width: 720,
  position_xy: [20,20],
  children: [
    _nilo = {
      color: blue,
      draw_hide: hide,
      shape: square,
      height: 128,
      width: 72,
      children: containers,
    },
    _scree,
  ],
  event_listner: { 
    on_click: greet_user(),
    on_long_press: [
      greet_uqser(),
      change_color(),
    ],
  },
}