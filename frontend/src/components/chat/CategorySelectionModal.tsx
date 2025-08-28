// frontend/src/components/chat/CategorySelectionModal.tsx

'use client';

import { useState, useEffect } from 'react';
import { useLanguage, useTranslations } from '@/hooks/useLanguage';
import styles from '@/styles/category-modal.module.css';

interface Category {
  categoryId?: number;
  categoryName?: string;
  text?: string;
  level?: number;
  children?: { [key: string]: Category } | any[];
}

interface Article {
  articleId: number;
  articleNo: string;
  supplierName: string;
  supplierId: number;
  articleProductName: string;
  imageLink?: string;
  s3ImageLink?: string;
}

interface ArticleWithInventory extends Article {
  in_stock: boolean;
  quantity_available: number;
  price_cop: number | null;
  discount_percentage: number;
}

interface CategorySelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCategorySelect: (data: {
    category_id: number;
    category_name: string;
    path: string[];
    articles: ArticleWithInventory[];
  }) => void;
  vehicleId: number;
  manufacturerId: number;
  categoryLevels: number;
  onSendMessage: (message: string) => void;
  onDataHandlerReady: (handler: (data: any) => void) => void;
}

export function CategorySelectionModal({
  isOpen,
  onClose,
  onCategorySelect,
  vehicleId,
  manufacturerId,
  categoryLevels,
  onSendMessage,
  onDataHandlerReady
}: CategorySelectionModalProps) {
  const { language } = useLanguage();
  const { t } = useTranslations();
  
  // State
  const [categories, setCategories] = useState<{ [key: string]: Category }>({});
  const [selectedPath, setSelectedPath] = useState<string[]>([]);
  const [selectedIds, setSelectedIds] = useState<(number | null)[]>([]);
  const [articles, setArticles] = useState<ArticleWithInventory[]>([]);
  const [loadingCategories, setLoadingCategories] = useState(false);
  const [loadingArticles, setLoadingArticles] = useState(false);
  const [searchTerms, setSearchTerms] = useState<string[]>([]);
  const [selectedArticles, setSelectedArticles] = useState<Set<number>>(new Set());
  
  // Set up data handler
  useEffect(() => {
    const handleData = async (data: any) => {
      try {
        console.log('[MODAL_DEBUG] Received data:', data.type, data);
        if (data.type === 'CATEGORIES_DATA') {
          console.log('[MODAL_DEBUG] Setting categories:', data.data?.categories);
          setCategories(data.data.categories || {});
          setLoadingCategories(false);
        } else if (data.type === 'ARTICLES_DATA') {
          // Fetch inventory for articles
          const articleIds = data.data.articles.map((a: Article) => a.articleId);
          await fetchInventory(articleIds, data.data.articles);
          setLoadingArticles(false);
        } else if (data.type === 'ERROR') {
          console.error('Backend error:', data.message);
          setLoadingCategories(false);
          setLoadingArticles(false);
        }
      } catch (error) {
        console.error('Error handling data:', error);
      }
    };

    onDataHandlerReady(handleData);
  }, [onDataHandlerReady]);

  // Load categories when modal opens
  useEffect(() => {
    console.log('[MODAL_DEBUG] Modal state changed - isOpen:', isOpen, 'vehicleId:', vehicleId, 'manufacturerId:', manufacturerId);
    if (isOpen && vehicleId && manufacturerId) {
      console.log('[MODAL_DEBUG] Loading categories for vehicle:', vehicleId, 'manufacturer:', manufacturerId);
      loadCategories();
    }
  }, [isOpen, vehicleId, manufacturerId]);

  // Load articles when final category is selected
  useEffect(() => {
    const shouldLoadArticles = selectedIds.length === categoryLevels && 
                              selectedIds[categoryLevels - 1] !== null;
    if (shouldLoadArticles) {
      loadArticles();
    }
  }, [selectedIds, categoryLevels]);

  const loadCategories = async () => {
    console.log('[MODAL_DEBUG] loadCategories called - setting loading to true');
    setLoadingCategories(true);
    try {
      const message = `GET_CATEGORIES:${vehicleId}:${manufacturerId}`;
      console.log('[MODAL_DEBUG] Sending message to backend:', message);
      onSendMessage(message);
    } catch (error) {
      console.error('[MODAL_DEBUG] Error loading categories:', error);
      setLoadingCategories(false);
    }
  };

  const loadArticles = async () => {
    const productGroupId = selectedIds[categoryLevels - 1];
    if (!productGroupId) return;
    
    setLoadingArticles(true);
    setArticles([]);
    
    try {
      onSendMessage(`GET_ARTICLES:${vehicleId}:${productGroupId}:${manufacturerId}`);
    } catch (error) {
      console.error('Error loading articles:', error);
      setLoadingArticles(false);
    }
  };

  const fetchInventory = async (articleIds: number[], articlesData: Article[]) => {
    try {
        const response = await fetch('/api/v1/inventory/articles', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('session_id')}`
        },
        body: JSON.stringify({ article_ids: articleIds })
        });

        if (response.ok) {
        const inventoryData = await response.json();
        
        // Check if any articles have stock
        const hasAnyStock = inventoryData.articles.some((inv: any) => inv.in_stock);
        
        if (!hasAnyStock) {
            // No stock available - send message to backend
            onSendMessage('NO_STOCK_AVAILABLE');
        }
        
        // Merge articles with inventory data
        const articlesWithInventory = articlesData.map(article => {
            const inventory = inventoryData.articles.find(
            (inv: any) => inv.article_id === article.articleId
            );
            
            return {
            ...article,
            in_stock: inventory?.in_stock || false,
            quantity_available: inventory?.quantity_available || 0,
            price_cop: inventory?.price_cop || null,
            discount_percentage: inventory?.discount_percentage || 0
            };
        });
        
        setArticles(articlesWithInventory);
        }
    } catch (error) {
        console.error('Error fetching inventory:', error);
        // Set articles without inventory data
        setArticles(articlesData.map(a => ({
        ...a,
        in_stock: false,
        quantity_available: 0,
        price_cop: null,
        discount_percentage: 0
        })));
        
        // Notify backend about inventory fetch failure
        onSendMessage('INVENTORY_CHECK_FAILED');
    }
};

  const getCurrentLevelCategories = (level: number): [string, Category][] => {
    if (level === 0) {
      return Object.entries(categories);
    }
    
    let current = categories;
    for (let i = 0; i < level; i++) {
      const key = selectedPath[i];
      if (!key || !current[key]) return [];
      
      const children = current[key].children;
      if (!children || Array.isArray(children) || typeof children !== 'object') {
        return [];
      }
      current = children;
    }
    
    return Object.entries(current);
  };

  const handleCategorySelect = (level: number, key: string, category: Category) => {
    const newPath = [...selectedPath.slice(0, level), key];
    const newIds = [...selectedIds.slice(0, level), category.categoryId || null];
    
    // Clear selections after this level
    setSelectedPath(newPath);
    setSelectedIds(newIds);
    setSearchTerms(prev => prev.slice(0, level + 1));
    
    // Clear articles if not at final level
    if (level < categoryLevels - 1) {
      setArticles([]);
    }
  };

  const handleArticleToggle = (articleId: number) => {
    setSelectedArticles(prev => {
      const newSet = new Set(prev);
      if (newSet.has(articleId)) {
        newSet.delete(articleId);
      } else {
        newSet.add(articleId);
      }
      return newSet;
    });
  };

  const handleConfirmSelection = () => {
    const selectedArticlesList = articles.filter(a => selectedArticles.has(a.articleId));
    
    onCategorySelect({
      category_id: selectedIds[categoryLevels - 1] || 0,
      category_name: selectedPath[selectedPath.length - 1] || '',
      path: selectedPath,
      articles: selectedArticlesList
    });
    
    onClose();
  };

  const filterCategories = (entries: [string, Category][], searchTerm: string) => {
    if (!searchTerm) return entries;
    
    return entries.filter(([key, cat]) => {
      const name = cat.text || cat.categoryName || key;
      return name.toLowerCase().includes(searchTerm.toLowerCase());
    });
  };

  const formatPrice = (price: number | null) => {
    if (!price) return 'N/A';
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP'
    }).format(price);
  };

  if (!isOpen) return null;

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2>{t('parts.categorySelection.title')}</h2>
          <button className={styles.closeButton} onClick={onClose}>×</button>
        </div>
        
        <div className={styles.modalBody}>
          {loadingCategories ? (
            <div className={styles.loading}>
              {t('parts.categorySelection.loading')}
            </div>
          ) : (
            <>
              {/* Category Dropdowns */}
              {Array.from({ length: categoryLevels }, (_, level) => {
                const entries = getCurrentLevelCategories(level);
                const isVisible = level === 0 || selectedIds[level - 1] !== null;
                
                if (!isVisible) return null;
                
                return (
                  <div key={level} className={styles.dropdownContainer}>
                    <label>
                      {t(`parts.categorySelection.level${level + 1}`) || `Level ${level + 1}`}
                    </label>
                    <input
                      type="text"
                      placeholder={t('parts.categorySelection.searchPlaceholder')}
                      value={searchTerms[level] || ''}
                      onChange={(e) => {
                        const newTerms = [...searchTerms];
                        newTerms[level] = e.target.value;
                        setSearchTerms(newTerms);
                      }}
                      className={styles.searchInput}
                    />
                    <select
                      value={selectedPath[level] || ''}
                      onChange={(e) => {
                        const key = e.target.value;
                        const category = entries.find(([k]) => k === key)?.[1];
                        if (category) {
                          handleCategorySelect(level, key, category);
                        }
                      }}
                      className={styles.dropdown}
                    >
                      <option value="">
                        {t('parts.categorySelection.selectCategory')}
                      </option>
                      {filterCategories(entries, searchTerms[level] || '').map(([key, cat]) => (
                        <option key={key} value={key}>
                          {cat.text || cat.categoryName || key}
                        </option>
                      ))}
                    </select>
                  </div>
                );
              })}

              {/* Articles List */}
              {articles.length > 0 && (
                <div className={styles.articlesContainer}>
                  <h3>{t('parts.categorySelection.availableArticles')}</h3>
                  
                  {loadingArticles ? (
                    <div className={styles.loading}>
                      {t('parts.categorySelection.loadingArticles')}
                    </div>
                  ) : (
                    <>
                      <div className={styles.articlesList}>
                        {articles.map(article => (
                          <div key={article.articleId} className={styles.articleItem}>
                            <input
                              type="checkbox"
                              checked={selectedArticles.has(article.articleId)}
                              onChange={() => handleArticleToggle(article.articleId)}
                              className={styles.checkbox}
                            />
                            
                            <div className={styles.articleInfo}>
                              <h4>{article.articleProductName}</h4>
                              <p className={styles.articleDetails}>
                                <span>{t('parts.articleNo')}: {article.articleNo}</span>
                                <span>{t('parts.supplier')}: {article.supplierName}</span>
                              </p>
                              
                              <div className={styles.inventoryInfo}>
                                <span className={article.in_stock ? styles.inStock : styles.outOfStock}>
                                  {article.in_stock 
                                    ? `${t('parts.inStock')} (${article.quantity_available})` 
                                    : t('parts.outOfStock')}
                                </span>
                                
                                {article.price_cop && (
                                  <span className={styles.price}>
                                    {formatPrice(article.price_cop)}
                                    {article.discount_percentage > 0 && (
                                      <span className={styles.discount}>
                                        {' '}(-{article.discount_percentage}%)
                                      </span>
                                    )}
                                  </span>
                                )}
                              </div>
                            </div>
                            
                            {article.s3ImageLink && (
                              <img 
                                src={article.s3ImageLink} 
                                alt={article.articleProductName}
                                className={styles.articleImage}
                              />
                            )}
                          </div>
                        ))}
                      </div>
                      
                      <div className={styles.modalFooter}>
                        <button 
                          className={styles.confirmButton}
                          onClick={handleConfirmSelection}
                          disabled={selectedArticles.size === 0}
                        >
                          {t('parts.categorySelection.confirmSelection')} ({selectedArticles.size})
                        </button>
                      </div>
                    </>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}