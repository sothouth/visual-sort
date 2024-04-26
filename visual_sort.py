from functools import *
import copy
import functools
from operator import pos
from threading import Timer
import tkinter as tk
import tkinter.messagebox as tkm
import random as rd

########################################################################

canvas_size=(1020,600)
canvas_space=10
canvas_rec_width=0

iconfigs:dict[str,tk.IntVar]={}
sconfigs:dict[str,tk.StringVar]={}

iconfigs_name=['num range left','num range right','run speed','nums length','random nums length','random num','run','end','comp counter','swap counter']
sconfigs_name=['now sorter']

should_normal=set()
should_clear=set()
should_draw=set()

color_normal='#646464'
color_focus='red'
color_right='green'

sorters=['插入排序','冒泡排序','堆排序','归并排序','快速排序','三数取中快排','三数取中直插快排']

nums=[]

timer=None

now_sort=None

########################################################################

class number:
    def __init__(self,pos:int,val:int)->None:
        self.rel_color=color_normal
        self.pos=pos
        self.val=val
        self.id=-1
        self.normal()

    def clear(self):
        if self.id!=-1:
            should_clear.add(self)

    def rel_clear(self):
        if self.id!=-1:
            canvas.delete(self.id)
            self.id=-1

    def draw(self):
        should_draw.add(self)

    def rel_draw(self):
        self.id=canvas.create_rectangle(canvas_space+(canvas_rec_width*self.pos),canvas_size[1],\
            canvas_space+(canvas_rec_width*(self.pos+1)),canvas_size[1]-self.val,\
            fill=self.color,width=0)

    def refreash(self):
        self.clear()
        self.draw()

    def focus_one_turn(self):
        should_normal.add(self)
        self.focus()

    def focus(self):
        self.color=color_focus
        self.refreash()

    def right(self):
        self.rel_color=color_right
        self.color=color_right
        self.refreash()

    def normal(self):
        self.color=color_normal
        self.refreash()

    def remove(self):
        new_number=copy.deepcopy(self)
        self.focus()
        self.refreash()
        return new_number
    
    def assign(self,new_number):
        iconfigs['swap counter'].set(iconfigs['swap counter'].get()+1)
        self.clear()
        self.val,self.color=new_number.val,new_number.color
        self.focus_one_turn()

    def swap(self,other):
        iconfigs['swap counter'].set(iconfigs['swap counter'].get()+1)
        self.val,other.val=other.val,self.val
        self.rel_color,other.rel_color=other.rel_color,self.rel_color
        self.focus_one_turn()
        other.focus_one_turn()

    def __lt__(self,other):
        iconfigs['comp counter'].set(iconfigs['comp counter'].get()+1)
        self.focus_one_turn()
        if type(other)==number:
            other.focus_one_turn()
            return self.val<other.val
        return self.val<other

    def __le__(self,other):
        iconfigs['comp counter'].set(iconfigs['comp counter'].get()+1)
        self.focus_one_turn()
        if type(other)==number:
            other.focus_one_turn()
            return self.val<=other.val
        return self.val<=other

    def __gt__(self,other):
        iconfigs['comp counter'].set(iconfigs['comp counter'].get()+1)
        self.focus_one_turn()
        if type(other)==number:
            other.focus_one_turn()
            return self.val>other.val
        return self.val>other

    def __ge__(self,other):
        iconfigs['comp counter'].set(iconfigs['comp counter'].get()+1)
        self.focus_one_turn()
        if type(other)==number:
            other.focus_one_turn()
            return self.val>=other.val
        return self.val>=other

    def __eq__(self,other):
        iconfigs['comp counter'].set(iconfigs['comp counter'].get()+1)
        self.focus_one_turn()
        if type(other)==number:
            other.focus_one_turn()
            return self.val==other.val
        return self.val==other

    def __ne__(self,other):
        iconfigs['comp counter'].set(iconfigs['comp counter'].get()+1)
        self.focus_one_turn()
        if type(other)==number:
            other.focus_one_turn()
            return self.val!=other.val
        return self.val!=other

    def __hash__(self):
        return hash(id(self))


def sort_dispatch(func):
    registry={}
    def register(sort_name,func=None):
        if func==None:
            return lambda f:register(sort_name,f)
        registry[sort_name]=func
        return func
    def wrapper(*args,**kvargs):
        return registry.get(sconfigs['now sorter'].get(),registry[object])(*args,**kvargs)
    registry[object]=func
    wrapper.register=register
    return wrapper

@sort_dispatch
def sort():
    return False

@sort.register(sorters[0])
def insert_sort():
    nums[0].right()
    yield
    for i in range(1,len(nums)):
        nums[i].right()
        for numl,numr in zip(nums[i-1::-1],nums[i:0:-1]):
            if numl<=numr:
                yield
                break
            numl.swap(numr)
            yield
    return

@sort.register(sorters[1])
def pop_sort():
    for i in range(1,len(nums)):
        for numl,numr in zip(nums[0:len(nums)-i],nums[1:len(nums)-i+1]):
            if numl>numr:
                numl.swap(numr)
            yield
        nums[len(nums)-i].right()
    nums[0].right()
    return

@sort.register(sorters[2])
def heap_sort():
    def build_max_heap():
        for i in range(((len(nums)-2)>>1),-1,-1):
            for _ in heapify(i,len(nums)):
                yield
    def heapify(now,end):
        max=(now<<1)+1
        rc=(now<<1)+2
        if rc<end and nums[max]<nums[rc]:
            max=rc
        yield
        if nums[now]<nums[max]:
            nums[now].swap(nums[max])
            yield
            if ((max<<1)+1)<end:
                for _ in heapify(max,end):
                    yield
        yield
    for _ in build_max_heap():
        yield
    for i in range(len(nums)-1,0,-1):
        nums[0].right()
        nums[0].swap(nums[i])
        yield
        for _ in heapify(0,i):
            yield
    nums[0].right()
    nums[0].swap(nums[1])
    yield

@sort.register(sorters[3])
def merge_sort():
    pass
@sort.register(sorters[4])
def quick_sort():
    def quick_sort_step(l,r):
        if l==r:
            nums[l].right()
            return
        if l+1==r:
            if nums[l]>nums[r]:
                nums[l].swap(nums[r])
            nums[l].right()
            nums[r].right()
            return
        ll,rr=l,r
        while l<r:
            while l<r and nums[r]>=nums[l]:
                r-=1
                yield
            nums[l].swap(nums[r])
            yield
            while l<r and nums[l]<nums[r]:
                l+=1
                yield
            nums[l].swap(nums[r])
            yield
        nums[l].right()
        if ll+1<l:
            for _ in quick_sort_step(ll,l-1):
                yield
        else:
            nums[ll].right()
        if l+1<rr:
            for _ in quick_sort_step(l+1,rr):
                yield
        else:
            nums[rr].right()
        yield
    for _ in quick_sort_step(0,len(nums)-1):
        yield

@sort.register(sorters[5])
def quick_2_sort():
    def quick_sort_step(l,r):
        if l==r:
            nums[l].right()
            return
        if l+1==r:
            if nums[l]>nums[r]:
                nums[l].swap(nums[r])
            nums[l].right()
            nums[r].right()
            return
        if l+2==r:
            if nums[l]>nums[l+1]:
                nums[l].swap(nums[l+1])
            yield
            if nums[l+1]>nums[r]:
                nums[l+1].swap(nums[r])
            yield
            if nums[l]>nums[l+1]:
                nums[l].swap(nums[l+1])
            nums[l].right()
            nums[l+1].right()
            nums[r].right()
            return
        mid=(l+r)>>1
        if nums[l]>nums[mid]:
            nums[l].swap(nums[mid])
        yield
        if nums[mid]>nums[r]:
            nums[mid].swap(nums[r])
        yield
        if nums[l]>nums[mid]:
            nums[l].swap(nums[mid])
        yield
        nums[l+1].swap(nums[mid])
        ll,rr=l,r
        l+=1
        while l<r:
            while l<r and nums[r]>=nums[l]:
                r-=1
                yield
            nums[l].swap(nums[r])
            yield
            while l<r and nums[l]<nums[r]:
                l+=1
                yield
            nums[l].swap(nums[r])
            yield
        nums[l].right()
        if ll+1<l:
            for _ in quick_sort_step(ll,l-1):
                yield
        else:
            nums[ll].right()
        if l+1<rr:
            for _ in quick_sort_step(l+1,rr):
                yield
        else:
            nums[rr].right()
        yield
    for _ in quick_sort_step(0,len(nums)-1):
        yield

@sort.register(sorters[6])
def quick_3_sort():
    def quick_sort_insert(l,r):
        nums[l].right()
        yield
        for i in range(l+1,r+1):
            ll=l
            rr=i-1
            while ll<=rr:
                mid=(ll+rr)>>1
                if nums[mid]>nums[i]:
                    rr=mid-1
                else:
                    ll=mid+1
                yield
            nums[i].right()
            for numl,numr in zip(nums[i-1:ll-1:-1],nums[i:ll:-1]):
                numl.swap(numr)
                yield
    def quick_sort_step(l,r):
        if l+15>r:
            for _ in quick_sort_insert(l,r):
                yield
            return
        mid=(l+r)>>1
        if nums[l]>nums[mid]:
            nums[l].swap(nums[mid])
        yield
        if nums[mid]>nums[r]:
            nums[mid].swap(nums[r])
        yield
        if nums[l]>nums[mid]:
            nums[l].swap(nums[mid])
        yield
        nums[l+1].swap(nums[mid])
        ll,rr=l,r
        l+=1
        while l<r:
            while l<r and nums[r]>=nums[l]:
                r-=1
                yield
            nums[l].swap(nums[r])
            yield
            while l<r and nums[l]<nums[r]:
                l+=1
                yield
            nums[l].swap(nums[r])
            yield
        nums[l].right()
        if ll+1<l:
            for _ in quick_sort_step(ll,l-1):
                yield
        else:
            nums[ll].right()
        if l+1<rr:
            for _ in quick_sort_step(l+1,rr):
                yield
        else:
            nums[rr].right()
        yield
    for _ in quick_sort_step(0,len(nums)-1):
        yield

def do_before():
    for num in should_normal:
        num.color=num.rel_color
        num.rel_clear()
        num.rel_draw()
    should_normal.clear()

def do_after():
    for num in should_clear:
        num.rel_clear()
    should_clear.clear()
    for num in should_draw:
        num.rel_draw()
    should_draw.clear()

def check_configs():
    if iconfigs['nums length'].get()<1:
        stop()
        tkm.showwarning(title='warnning',message='数组长度过小')
        return False
    if iconfigs['num range left'].get()>iconfigs['num range right'].get():
        stop()
        tkm.showwarning(title='warnning',message='取值范围无效')
        return False

    return True

def step():
    if  not check_configs():
        return
    if iconfigs['end'].get()==1:
        remake()
    try:
        do_before()
        next(now_sort)
        do_after()
    except StopIteration:
        do_after()
        iconfigs['end'].set(1)
        end()
        return False
    else:
        return True

def run():
    if iconfigs['end'].get()==1:
        remake()
    if iconfigs['run'].get()==0:
        iconfigs['run'].set(1)
        runt()

def runt():
    try:
        if (iconfigs['run'].get()==1) and step():
            Timer(iconfigs['run speed'].get()/1000,runt).start()
        else:
            iconfigs['run'].set(0)
    except:
        return


def stop():
    iconfigs['run'].set(0)

def end():
    tkm.showinfo(title='message',message='排序已完成')

def new_nums():
    global nums
    canvas.delete(tk.ALL)
    del nums
    should_normal.clear()
    should_clear.clear()
    should_draw.clear()
    if iconfigs['random num'].get()==1:
        rl,rr=iconfigs['num range left'].get(),iconfigs['num range right'].get()
        nums=[number(pos,rd.randint(rl,rr)) for pos in range(iconfigs['nums length'].get())]
    else:
        pos_nums=[pos for pos in range(1,iconfigs['nums length'].get()+1)]
        rd.shuffle(pos_nums)
        nums=[number(pos,pos_num) for pos,pos_num in enumerate(pos_nums)]
    do_after()

def remake():
    if  not check_configs():
        return
    global now_sort
    global nums
    global canvas_rec_width
    canvas_rec_width=(canvas_size[0]-canvas_space*2)/iconfigs['nums length'].get()
    iconfigs['run'].set(0)
    iconfigs['end'].set(0)
    iconfigs['swap counter'].set(0)
    iconfigs['comp counter'].set(0)
    if iconfigs['random nums length'].get()==1:
        iconfigs['nums length'].set(rd.randint(10,30))
    new_nums()
    now_sort=sort()


def f_nums_set():
    if iconfigs['random num'].get()==1:
        iconfigs['num range left'].set(20)
        e_nums_l.config(state='normal')
        iconfigs['num range right'].set(30)
        e_nums_r.config(state='normal',textvariable=iconfigs['num range right'])
    else:
        iconfigs['num range left'].set(1)
        e_nums_l.config(state='readonly')
        e_nums_r.config(state='readonly',textvariable=iconfigs['nums length'])

def change_sorter():
    mb_select.config(text=sconfigs['now sorter'].get())
    root.title(sconfigs['now sorter'].get()+'可视化演示 --power by sothouth')
    remake()


########################################################################

root=tk.Tk()

for name in iconfigs_name:
    iconfigs[name]=tk.IntVar(root)

for name in sconfigs_name:
    sconfigs[name]=tk.StringVar(root)

canvas=tk.Canvas(root,width=canvas_size[0],height=canvas_size[1])
canvas.grid(row=0,column=0)

console=tk.Frame(root)
console.grid(row=1,column=0)

frame_len=tk.Frame(console)
frame_len.grid(row=0,column=0,sticky='W')
bc_len=tk.Checkbutton(frame_len,text='random',variable=iconfigs['random nums length'])
bc_len.grid(row=0,column=0)
l_len=tk.Label(frame_len,text='length:')
l_len.grid(row=0,column=1)
iconfigs['nums length'].set(30)
e_len=tk.Entry(frame_len,textvariable=iconfigs['nums length'])
e_len.grid(row=0,column=2)

frame_nums=tk.Frame(console)
frame_nums.grid(row=1,column=0,sticky='W')
bc_nums=tk.Checkbutton(frame_nums,text='random',variable=iconfigs['random num'],command=f_nums_set)
bc_nums.select()
bc_nums.grid(row=0,column=0)
l_nums=tk.Label(frame_nums,text='range:')
l_nums.grid(row=0,column=1)
iconfigs['num range left'].set(20)
e_nums_l=tk.Entry(frame_nums,textvariable=iconfigs['num range left'],width=10)
e_nums_l.grid(row=0,column=2)
iconfigs['num range right'].set(30)
e_nums_r=tk.Entry(frame_nums,textvariable=iconfigs['num range right'],width=10)
e_nums_r.grid(row=0,column=3)

frame_cmd=tk.Frame(console)
frame_cmd.grid(row=0,column=2,rowspan=2)
frame_speed=tk.Frame(frame_cmd)
frame_speed.grid(row=0,column=0,columnspan=3)
l_speed=tk.Label(frame_speed,text='speed(ms):')
l_speed.grid(row=0,column=0)
iconfigs['run speed'].set(300)
e_speed=tk.Entry(frame_speed,textvariable=iconfigs['run speed'],width=10)
e_speed.grid(row=0,column=1)
b_step=tk.Button(frame_cmd,text='step',command=step,width=5)
b_step.grid(row=1,column=0)
iconfigs['run'].set(0)
b_run=tk.Button(frame_cmd,text='run',command=run,width=5)
b_run.grid(row=1,column=1)
b_stop=tk.Button(frame_cmd,text='stop',command=stop,width=5)
b_stop.grid(row=1,column=2)

frame_select=tk.Frame(console)
frame_select.grid(row=0,column=3,rowspan=2)
mb_select=tk.Menubutton(frame_select,text=sorters[0],relief="raised")
mb_select.grid(row=0,column=0)
m_select=tk.Menu(mb_select)
mb_select.config(menu=m_select)
sconfigs['now sorter'].set(sorters[0])
root.title(sconfigs['now sorter'].get()+'可视化演示 --power by sothouth')
for sorter in sorters:
    m_select.add_radiobutton(label=sorter,value=sorter,variable=sconfigs['now sorter'],command=change_sorter)

frame_counter=tk.Frame(console)
frame_counter.grid(row=0,column=4,rowspan=2)
l_move=tk.Label(frame_counter,text='comp:')
l_move.grid(row=0,column=0)
lc_move=tk.Label(frame_counter,textvariable=iconfigs['comp counter'],width=10,anchor='e')
lc_move.grid(row=0,column=1)
l_swap=tk.Label(frame_counter,text='swap:')
l_swap.grid(row=1,column=0)
lc_swap=tk.Label(frame_counter,textvariable=iconfigs['swap counter'],width=10,anchor='e')
lc_swap.grid(row=1,column=1)

frame_remake=tk.Frame(console)
frame_remake.grid(row=0,column=5,rowspan=2)
b_remake=tk.Button(frame_remake,text='remake',command=remake)
b_remake.grid(row=0,column=0)

remake()

root.mainloop()

