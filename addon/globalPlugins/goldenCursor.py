﻿# -*- coding: utf-8 -*-
#golden cursor
# Copyright (C) 2015-2016 
#Version 1.1dev
#License GNU GPL
# Date: 25/12/2015
#team work: author : salah atair, translation and keycommands are made by wafeeq taher
# Additional tweaking done by Joseph Lee and contributors, resetting version to 1.0.
#now it became easy to control the mouse using keyboard

import codecs
from threading import Timer
import winsound 
import wx
import gui
import os
import speech
import time
import tones
import globalPluginHandler
import mouseHandler
import ui
import api
import win32api

import addonHandler
addonHandler.initTranslation()
filesPath = os.path.join(os.path.dirname(__file__), 'files')
isOpened = 0
class positionsList(gui.SettingsDialog):
	title = _("positions List")
	def __init__(self, parent):
		super(positionsList, self).__init__(parent)

	def __del__(self):
		super(positionsList, self).__del__()
		global isOpened
		if isOpened == 1:
			isOpened = 0

	def makeSettings(self, sizer):
		appName = api.getForegroundObject().appModule.appName
		self.path = os.path.join(filesPath, appName+'.gc')
		with codecs.open(self.path,'r','utf-8') as f:
			self.data = f.read().strip()
		self.data = self.data.split(u'\n')
		listBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
		st = wx.StaticText(self,-1,_('choose a item of this list'))
		listBoxSizer.Add(st)
		self.listBox = wx.ListBox(self,-1)
		listBoxSizer.Add(self.listBox)
		sizer.Add(listBoxSizer)
		for i in self.data:
			if i [0] == u'[':
				self.listBox.Append(i[1:-1], self.data [self.data.index(i)+1])
		buttonsSizer = wx.BoxSizer(wx.HORIZONTAL)
		b_rename = wx.Button(self, -1,_('&rename'))
		buttonsSizer.Add(b_rename)
		b_delete = wx.Button(self, -1,_('&delete'))
		buttonsSizer.Add(b_delete)
		b_clear = wx.Button(self, -1,_('&clear'))
		buttonsSizer.Add(b_clear)
		b_rename.Bind(wx.EVT_BUTTON, self.onRename)
		b_delete.Bind(wx.EVT_BUTTON, self.onDelete)
		b_clear.Bind(wx.EVT_BUTTON, self.onClear)
		sizer.Add(buttonsSizer)

	def postInit(self):
		self.listBox.SetFocus()

	def onRename(self, event):
		if self.listBox.IsEmpty():
			ui.message(_('the list is empty.'))
			return
		try:
			index = self.data.index(u'['+self.listBox.GetStringSelection()+u']')
		except:
			ui.message(_('no selection'))
			return

		oldName = self.listBox.StringSelection
		name = wx.GetTextFromUser(_('you can rename this name.'),_('Rename'),self.listBox.StringSelection)
		# When escape is pressed, an empty string is returned.
		if name == "" or name == oldName:
			return
		self.listBox.SetFocus()
		x_y = self.listBox.GetClientData(self.listBox.GetSelection())
		del self.data [index]
		self.data.insert(index, u'['+name+u']')
		data = u'\n'.join(self.data)
		with codecs.open(self.path,'w','utf-8') as f:
			f.write(data)
		i = self.listBox.GetSelection()
		self.listBox.Delete(i)
		self.listBox.Insert(name,i)
		self.listBox.SetClientData(i,x_y)
		self.listBox.SetSelection(i)
	def onDelete(self,event):
		if self.listBox.IsEmpty():
			ui.message(_('the list is empty.'))
			return
		try:
			index = self.data.index(u'['+self.listBox.GetStringSelection()+u']')
		except:
			ui.message(_('no selection'))
			return
		del self.data [index]
		del self.data [index]
		ui.message(_('the position has been deleted.'))
		data = u'\n'.join(self.data)
		with codecs.open(self.path,'w','utf-8') as f:
			f.write(data)
		self.listBox.Delete(self.listBox.GetSelection())
		if self.listBox.IsEmpty():
			os.remove(self.path)

	def onClear(self, event):
		try:
			os.remove(self.path)
		except:
			ui.message(_('The list is empty'))
		self.listBox.Clear()
		ui.message(_('the list has been cleared.'))

	def onOk(self, event):
		super(positionsList, self).onOk(event)
		try:
			x, y= self.listBox.GetClientData(self.listBox.GetSelection()).split(u',')
		except:
			return
		x =int(x)
		y = int(y)
		win32api.SetCursorPos((x,y))
		t = Timer(0.5, mouseHandler.executeMouseMoveEvent,[x, y])
		t.start()
		self.Close()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = u"golden cursor"
	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)
		self.pixelMoving =5
		self.sayPixel = 1
		self.getAppRestriction = None
		self.restriction = 0

	def script_savedPositionsList(self, gesture):
		global isOpened 
		
		if isOpened == 1:
			ui.message(_('An NVDA settings dialog is already open. Please close it first.'))
			return
		else:
			isOpened = 1
		if api.getForegroundObject().appModule.appName+'.gc' in os.listdir(filesPath):
			gui.mainFrame._popupSettingsDialog(positionsList)
		else:
			ui.message(_('there is no saved data for this application.'))

	script_savedPositionsList.__doc__ = _('To open a list showing the points that have already been saved for this application.')

	def script_savePosition(self, gesture):
		d = wx.TextEntryDialog(gui.mainFrame, _("Enter the value for position name you wish to save."), _("save position"))
		def callback(result):
			if result == wx.ID_OK:
				wx.CallLater(100,self.saving, d.GetValue())
		gui.runScriptModalDialog(d, callback)
	def saving(self,name):
		name = name.rstrip()
		speech.cancelSpeech()
		if name == u'':
			wx.CallAfter(gui.messageBox, _("please enter the value for the name of the position."), _("Error"), wx.OK|wx.ICON_ERROR)
			return
		x, y = win32api.GetCursorPos()
		appName = self.getMouse().appModule.appName
		path = os.path.join(filesPath, appName+'.gc')
		name = '['+name+']'
		p = name+'\n'+str(x)+','+str(y)
		try:
			with codecs.open(path,'r','utf-8') as f:
				data = f.read().strip()
		except Exception ,e:
			data = u''
		if name in data:
			data = data.split('\n')
			i = data.index(name)
			del data [i]
			del data [i]
			data = '\n'.join(data)
			p = data+u'\n'+p
		else:
			p = data+u'\n'+p
		with codecs.open(path,'w','utf-8') as f:
			f.write(p)
			ui.message(_("the position has been saved in %s." %(path)))
	script_savePosition.__doc__ = _('to save a the current position.')

	def script_mouseMovementChange (self, gesture):
		list = [1,5,10,20,50,100]
		index = list.index(self.pixelMoving)
		try:
			self.pixelMoving = list[index+1]
		except:
			self.pixelMoving = list[0]
		ui.message(str(self.pixelMoving))
	script_mouseMovementChange.__doc__ = _('to select a value for mouse movement (1, 10, 20, 50. 100.')

	def script_toggleSpeakPixels(self, gesture):
		if self.sayPixel == 1:
			self.sayPixel =0
			ui.message(_('report pixels off'))
			tones.beep(500,200)
		else:
			self.sayPixel =1
			ui.message(_('report pixels on'))
			tones.beep(1000,200)
	script_toggleSpeakPixels.__doc__ = _('toggle reporting of pixels')

	def script_sayPosition(self,gesture):
		x, y = win32api.GetCursorPos()
		str = _('%d , %d' %(x,y)) 
		ui.message(str)
	script_sayPosition.__doc__ = _('report the positions of the mouse.')

	def script_moveMouseRight(self,gesture):
		self.move_mouse(1)
	script_moveMouseRight.__doc__ = _('Moves the Mouse pointer right.')

	def script_moveMouseLeft(self,gesture):
		self.move_mouse(2)
	script_moveMouseLeft.__doc__ = _('Moves the Mouse pointer left.')

	def script_moveMouseUp(self,gesture):
		self.move_mouse(4)
	script_moveMouseUp.__doc__ = _('Moves the Mouse pointer up.')

	def script_moveMouseDown(self,gesture):
		self.move_mouse(3)
	script_moveMouseDown.__doc__ = _('Moves the Mouse pointer down.')

	def script_goToPosition(self,gesture):
		d = wx.TextEntryDialog(gui.mainFrame, _("Enter the value for position number you wish to jump to"), _("Jump to position"))
		def callback(result):
			if result == wx.ID_OK:
				wx.CallLater(100,self.jumping, d.GetValue())
		gui.runScriptModalDialog(d, callback)
	def jumping(self,num):
		speech.cancelSpeech()
		if ',' not in num:
			wx.CallAfter(gui.messageBox, _("please enter comma between the first and the second number"), _("Error"), wx.OK|wx.ICON_ERROR)
			return
		num = num.replace(' ','')
		num = num.split(',')
		x = num [0]
		y = num [1]
		if x.isdigit() == False or y.isdigit() == False:
			wx.CallAfter(gui.messageBox, _("please enter an integer number."), _("Error"), wx.OK|wx.ICON_ERROR)
			return
		x = int(x)
		y = int(y)
		win32api.SetCursorPos((x,y))
		self.getMouse()
		ui.message(str(x)+','+ str(y))
	script_goToPosition.__doc__ = _('type the x/y value you wish the cursor to jump to')
	def script_toggleMouseRestriction(self,gesture):
		self.getAppRestriction = self.getMouse()
		if self.restriction == 0:
			self.restriction = 1 
			ui.message(_('restriction on'))
			tones.beep(1000,200)
		else:
			self.restriction = 0
			ui.message(_('restriction off'))
			tones.beep(500,200)
	script_toggleMouseRestriction.__doc__ = _('Toggles the restriction between the 2 levels you can toggle between Application Window restriction and Unrestricted.')

	def move_mouse(self,d):
		w, h = win32api.GetMonitorInfo(1) ['Monitor'][2:]
		x , y= win32api.GetCursorPos()
		oldX = x
		oldY = y
		if d == 1:
			x = x+self.pixelMoving
			pos = str(x)
		elif d == 2:
			x = x- self.pixelMoving
			pos = str(x)
		elif d == 3:
			y = y+self.pixelMoving
			pos = str(y)
		elif d == 4:
			y = y-self.pixelMoving
			pos = str(y)
		o =api.getMouseObject()
		if x in range(0,w) and y in range(0,h):
			win32api.SetCursorPos((x,y))
			mouseHandler.executeMouseMoveEvent(x, y)
		else:
			winsound.MessageBeep(0)
			return
		if self.restriction == 1 and self.getAppRestriction.appModule.appName != self.getMouse().appModule.appName:
			winsound.MessageBeep(0)
			win32api.SetCursorPos((oldX,oldY))
			mouseHandler.executeMouseMoveEvent(oldX, oldY)
			if self.getAppRestriction.appModule.appName != self.getMouse().appModule.appName:
				x,y, w, h = self.getAppRestriction.location
				win32api.SetCursorPos((x,y))
				mouseHandler.executeMouseMoveEvent(x, y)
			return
		if self.sayPixel == 1:
			ui.message(pos)
		else:
			pass

 	def getMouse(self):
		x , y= win32api.GetCursorPos()
		o = api.getDesktopObject().objectFromPoint(x,y)
		return o


	__gestures = {
	"kb:nvda+windows+c":"mouseMovementChange",
	"kb:nvda+windows+rightarrow":"moveMouseRight",
	"kb:nvda+windows+leftarrow":"moveMouseLeft",
	"kb:nvda+windows+upArrow":"moveMouseUp",
	"kb:nvda+windows+downArrow":"moveMouseDown",
	"kb:nvda+windows+j":"goToPosition",
	"kb:nvda+windows+p":"sayPosition",
	"kb:nvda+windows+s":"toggleSpeakPixels",
	"kb:nvda+windows+r":"toggleMouseRestriction",
		"kb:nvda+shift+l": "savePosition",
		"kb:nvda+control+l": "savedPositionsList",

	}
