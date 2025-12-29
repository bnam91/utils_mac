-- 알림 센터의 특정 알림 그룹 클릭
-- 경로: Application{"알림 센터"} -> AXWindows[0]Window{"알림 센터"} -> AXChildren[0]Group{""} 
--      -> AXChildren[0]Group{""} -> AXChildren[0]ScrollArea{""} -> AXChildren[0]Group{"AXNotificationListItems"} 
--      -> AXChildren[2]Group{"메시지 , "}

on run
	try
		-- 알림 센터 애플리케이션에 접근
		tell application "System Events"
			tell process "NotificationCenter"
				-- 알림 센터가 열려있는지 확인
				if not (exists window "알림 센터") then
					-- display notification "알림 센터를 먼저 열어주세요" with title "알림"
					return
				end if
				
				-- 제공된 경로를 정확히 따라가기
				-- Application{"알림 센터"} -> AXWindows[0]Window{"알림 센터"}
				tell window "알림 센터"
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
									-- AXChildren[2]Group{"메시지 , "}
									-- 인덱스는 1부터 시작하므로 [2]는 세 번째 요소 (group 3)
									set groupCount to count of groups of notificationListGroup
									
									if groupCount > 2 then
										set notificationGroup to group 3 of notificationListGroup
										
										-- 그룹 클릭
										click notificationGroup
										display notification "알림 그룹 클릭 완료 (인덱스 2)" with title "성공"
										return "알림 그룹 클릭 완료"
									else if groupCount > 1 then
										-- 인덱스 2가 없으면 두 번째 그룹 사용
										set notificationGroup to group 2 of notificationListGroup
										click notificationGroup
										display notification "인덱스 2 그룹이 없어 두 번째 그룹 클릭 (총 그룹 개수: " & groupCount & ")" with title "알림"
										return "두 번째 그룹 클릭 완료"
									else
										error "알림 그룹을 찾을 수 없습니다 (그룹 개수: " & groupCount & ")"
									end if
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
