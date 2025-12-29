-- 알림 센터의 "모두 지우기" 버튼 클릭 (모든 알림 삭제)
-- 경로: Application{"알림 센터"} -> AXWindows[0]Window{"알림 센터" 또는 "Notification Center"} 
--      -> AXChildren[0]Group{""} -> AXChildren[0]Group{""} -> AXChildren[0]ScrollArea{""} 
--      -> AXChildren[0]Group{"AXNotificationListItems"} -> AXChildren[1]Button{"" 또는 "모두 지우기"}

on run
	try
		-- 알림 센터 애플리케이션에 접근
		tell application "System Events"
			tell process "NotificationCenter"
				-- 알림 센터가 열려있는지 확인 (한글/영어 둘 다 확인)
				set notificationWindow to null
				if (exists window "알림 센터") then
					set notificationWindow to window "알림 센터"
				else if (exists window "Notification Center") then
					set notificationWindow to window "Notification Center"
				else
					-- display notification "알림 센터를 먼저 열어주세요" with title "알림"
					return
				end if
				
				-- 제공된 경로를 정확히 따라가기
				-- Application{"알림 센터"} -> AXWindows[0]Window{"알림 센터" 또는 "Notification Center"}
				tell notificationWindow
					-- AXChildren[0]Group{""}
					set firstGroup to group 1
					
					-- AXChildren[0]Group{""}
					tell firstGroup
						set secondGroup to group 1
						
						-- AXChildren[0]ScrollArea{""}
						tell secondGroup
							set scrollArea to scroll area 1
							
							-- AXChildren[0]Group{"AXNotificationListItems"}
							tell scrollArea
								-- 그룹 이름으로 찾기 시도
								set notificationListGroup to null
								try
									set notificationListGroup to group "AXNotificationListItems"
								on error
									-- 이름으로 찾을 수 없으면 첫 번째 그룹 사용
									if (count of groups) > 0 then
										set notificationListGroup to group 1
									end if
								end try
								
								if notificationListGroup is not null then
									-- AXChildren[1]Button{"" 또는 "모두 지우기"}
									-- 인덱스는 1부터 시작하므로 [1]은 두 번째 요소 (button 2)
									set clearAllButton to null
									
									-- 방법 1: 이름으로 찾기 시도 ("모두 지우기")
									try
										set clearAllButton to button "모두 지우기" of notificationListGroup
									end try
									
									-- 방법 2: 이름으로 찾을 수 없으면 인덱스로 찾기 (AXChildren[1] = button 2)
									if clearAllButton is null then
										if (count of buttons of notificationListGroup) > 1 then
											set clearAllButton to button 2 of notificationListGroup
										else if (count of buttons of notificationListGroup) > 0 then
											-- 버튼이 하나만 있으면 그것 사용
											set clearAllButton to button 1 of notificationListGroup
										else
											error "모두 지우기 버튼을 찾을 수 없습니다"
										end if
									end if
									
									-- 버튼 클릭
									click clearAllButton
									return "모두 지우기 버튼 클릭 완료"
								else
									error "AXNotificationListItems 그룹을 찾을 수 없습니다"
								end if
							end tell
						end tell
					end tell
				end tell
			end tell
		end tell
	on error errorMessage
		-- display notification "오류: " & errorMessage with title "스크립트 오류"
		return "오류: " & errorMessage
	end try
end run
