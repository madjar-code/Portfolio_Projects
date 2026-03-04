import React, { useState, useRef, useEffect } from 'react'
import styled from 'styled-components'

const MenuContainer = styled.div`
  position: relative;
`

const MenuButton = styled.button`
  padding: ${({ theme }) => theme.spacing.xs} ${({ theme }) => theme.spacing.sm};
  background: ${({ theme }) => theme.colors.backgroundDark};
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  font-size: 18px;
  line-height: 1;
  color: ${({ theme }) => theme.colors.text};
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;

  &:hover {
    background: ${({ theme }) => theme.colors.border};
  }

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    width: 36px;
    height: 36px;
    font-size: 20px;
  }
`

const MenuDropdown = styled.div<{ isOpen: boolean }>`
  position: absolute;
  top: calc(100% + ${({ theme }) => theme.spacing.xs});
  right: 0;
  background: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 160px;
  z-index: 100;
  display: ${({ isOpen }) => (isOpen ? 'block' : 'none')};
  overflow: hidden;

  @media (min-width: ${({ theme }) => theme.breakpoints.tablet}) {
    min-width: 180px;
  }
`

const MenuItem = styled.button<{ variant?: 'danger' }>`
  width: 100%;
  padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.md};
  text-align: left;
  font-size: 14px;
  color: ${({ variant, theme }) =>
    variant === 'danger' ? theme.colors.danger : theme.colors.text};
  background: none;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.sm};

  &:hover {
    background: ${({ theme }) => theme.colors.backgroundDark};
  }

  &:not(:last-child) {
    border-bottom: 1px solid ${({ theme }) => theme.colors.border};
  }
`

interface MenuOption {
  label: string
  icon?: React.ReactNode
  onClick: () => void
  variant?: 'danger'
}

interface Props {
  options: MenuOption[]
}

export const DropdownMenu: React.FC<Props> = ({ options }) => {
  const [isOpen, setIsOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {

    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const handleMenuClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    setIsOpen(!isOpen)
  }

  const handleOptionClick = (e: React.MouseEvent, onClick: () => void) => {
    e.stopPropagation()
    onClick()
    setIsOpen(false)
  }

  return (
    <MenuContainer ref={menuRef}>
      <MenuButton onClick={handleMenuClick}>⋯</MenuButton>
      <MenuDropdown isOpen={isOpen}>
        {options.map((option, index) => (
          <MenuItem
            key={index}
            variant={option.variant}
            onClick={(e) => handleOptionClick(e, option.onClick)}
          >
            {option.icon && <span style={{ display: 'flex', alignItems: 'center' }}>{option.icon}</span>}
            {option.label}
          </MenuItem>
        ))}
      </MenuDropdown>
    </MenuContainer>
  )
}