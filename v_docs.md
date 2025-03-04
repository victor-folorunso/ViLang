***Vi Language Documentation***

**overview**
v is a very simple cross_platform app development focused language
code.v + transpiler -> code.c++
code.c++  -> cross platform executable

the v transpiler is a python software that converts the code written in v,into one of c++ 


**Comments**
<# 
  this,
  is a multi-line comment 
  in v
#>

#this is a single line comment in v

**Naming conventions**
generally,it closely resembles python (ie snake case), 
however,containers start  with an underscore 
ie _containerName1


**containers **
v is all about containers.each container is styled by giving it attributes
Each container in V is styled using the syntax below
when nested,the inner container is called a child   while the outer is called parent.
the child container inherits some properties from the parent (except specifically told not to)

_screen1: {
  color: red,
  draw_hide:draw,
  shape: square,
  height: 128,
  width: 72,
  position_xy: [20,20],
}  

Two containers can have the same style when separated using a coma 

_container1, _container2 = {
  color: red,
  draw_hide:draw,
  shape: square,
  height: 128,
  width: 72,
  position_xy: [20,20],
}  

** functions**
a user defined function is defined like this 
do_as_user_says(){code logics}   

greet_user(_container){
  for (child in _container.children){
    child = {
      color: rgb(120,7,7),
      width: child.width + 12
    }
  } 
}   

and is called like this 
do_as_user_says()

while inbuilt functions are used directly. ie visit(url),play(url),etc
this is because the action to be performed when the function is called has already been pre_specified.
the event listner attribute of a container usually houses functions (using keywords for specific events).
some keywords are on_collide,on_click


main _screen = {                         
  color: green,              
  height: 1280,
  width: 720,
  children: [
    _search_bar,
    _blank_body,
  ],
  event_listner: { 
    on_click: greet_user(),
    on_long_press: [
      greet_user(),
      visit(url to webpage),
    ],
    on_swipe_down: play(url to item)
    on_swipe_left: change_color(),
    on_collide: {
      [object1, object2, objectn]: [play(url),greet_user()],
      [object1, object2]: [action]
    }
  },
}

**main**
the main container is the first container to be parsed.
the main container is defined using the main keyword followed by the container id. 
all auxiliary containers are drawn directly or indirectly inside the main container 
the main container is to be in a main.v file. all other containers and functions are imported into this main.v file

**attributes (keywords and values)**
no units are needed when  working   with attributes of a container.by default the main container is   given a   width and height of the videowport  while other containers drawa wn 
in it are given relative height and  width to the parent container.
instead of specifying unit(if needed),the developer can just specify a different parent for that container 
Note: when containers are styled and there is conflict, the program crashes rather than infer

model of an attribute
key: value
key1,key2: value1, value2

**key**                          **value type**     **default**                **NOTE**                                                         
  scrollable                       bool                                          determines if  the container is scrollable or not

  draw_hide                        draw / hide                                   used to set if the container is displayed or not.

  shape                                               square                     others are sqircle,circle,cube(3d shape),etc   

  width                                               10                         value must be specified except if styled to scroll.
                                                                                 A fixed page(ie game or app) must have definite width and height

  color                                                                          it can also be rgb()

  position                                                                       can be right, left, top, bottom, right, bottom and right, middle, 
                                                                                 coordinate(X,Y),coordinate(X,Y,Z)
                                                                                 when using coordinate position,the x, y and optional z arguments specify percentage of height and width,not pixel
                                                                                 thus the higest value of x,y or z is 100
                                                                                 e.t.c 
  z_index                                                                        z_index allows for one container to be drawn over another.
                                                                                 a container with z_index of 1 would draw over an container with z_index of 0.
 
  content_align                                                                  not center due to British English confusion. it is used to center text
  
  content_padding                                                                use this to shrink content into the middle.
  
  content_padding_top                                                            shrink the content smaller and towards a single side (to the bottom) 
  
  content_padding_color
  
  content_padding_color_z_index

  type                                                                           style can be button, link, search bar scroller,icon 
                                                                                 button and link  e.t.c
                                                                                 
  text_content:                                                                  example ->  "Hello {concatenated_var}
                                                                                              text written in v can span multiple lines,
                                                                                              however the text can be wrapped by the editor"  
                                                                                 other types of content are audio_content and video_content
  text_content_font

  background_image                                                               takes a url ie  \url\to\image

  child_container
  
  children_align
  
  children_padding

  repeat_by                      int,int                                       this is used to repeat items it repeats the given item in x, y
                                                                               (ie making a grid of containers   without explicitly creating each container). 
                                                                               it creates numerous containers.each,take the parent container name,
                                                                               an underscore and its coordinate,as its own nmae.
                                                                               ie _parent_container_name_X1Y1 
                                                                               it can alqso be uqsed to create 3d containerqs uqsing type int,int,int and each are acceqsqsed uqsing xyz coordinateqs


example uqsing repeat_by attribute

_scree: {
  color: red,
  draw_hide:draw,
  shape: square,
  height: 128,
  width: 72,
  position_xy: [20,20],
  repeat_by: 4,4
}  

then each of the children can be accessed thus

change_color(){
  _scree.children.X1Y1: new_style
}

wait_sec(3) 
tells program to delay action for some seconds

updating the static page
a static page is drawn usually the main container. after changes are made to any of the visible screen containers, the container is automatically redrawn  
